import math 
import re

import maya

from PySide2 import QtCore
from PySide2 import QtWidgets

import altmaya
from altmaya import tools


class Cubic:
    def __init__(self, p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):
        self.p1x = p1x; self.p1y = p1y
        self.p2x = p2x; self.p2y = p2y
        self.p3x = p3x; self.p3y = p3y
        self.p4x = p4x; self.p4y = p4y
    def angleLeft(self): xd = self.p2x - self.p1x; yd = self.p2y - self.p1y; return math.atan2(yd, xd)
    def angleRight(self): xd = self.p4x - self.p3x; yd = self.p4y - self.p3y; return math.atan2(yd, xd)
    def weightLeft(self): xd = self.p2x - self.p1x; yd = self.p2y - self.p1y; return math.sqrt(yd * yd + xd * xd)
    def weightRight(self): xd = self.p4x - self.p3x; yd = self.p4y - self.p3y; return math.sqrt(yd * yd + xd * xd)


class SalientPosesGUI(altmaya.StandardMayaWindow):

    def __init__(self):
        super(SalientPosesGUI, self).__init__("Salient Poses")
        
        self.extreme_selections = {}
        self.breakdown_selections = {}
        self.current_selection = []
        self.select_attr_gui = tools.AttributeSelector("Choose Attributes for Selection", [], parent=self)
        self.reduce_attr_gui = tools.AttributeSelector("Choose Attributes for Reduction", [], parent=self)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.choose_select_attr_button = QtWidgets.QPushButton("Attrs (S)")
        self.choose_reduce_attr_button = QtWidgets.QPushButton("Attrs (R)")
        
        self.fixed_keyframes_label = QtWidgets.QLabel("Fixed Keyframes")
        self.fixed_keyframes_edit = QtWidgets.QLineEdit()
        
        self.select_extremes_button = QtWidgets.QPushButton("Extremes")
        self.n_extreme_keyframes_label = QtWidgets.QLabel("N")
        self.n_extreme_keyframes_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.n_extreme_keyframes_edit = QtWidgets.QLineEdit(str(self.n_extreme_keyframes_slider.value()))
        self.n_extreme_keyframes_edit.setEnabled(False)
        self.extreme_reduce_button = QtWidgets.QPushButton("Reduce by Extremes Only")
        
        self.select_breakdowns_button = QtWidgets.QPushButton("Breakdowns")
        self.n_breakdown_keyframes_label = QtWidgets.QLabel("N")
        self.n_breakdown_keyframes_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.n_breakdown_keyframes_edit = QtWidgets.QLineEdit(str(self.n_breakdown_keyframes_slider.value()))
        self.n_breakdown_keyframes_edit.setEnabled(False)
        self.breakdown_reduce_button = QtWidgets.QPushButton("Reduce by Breakdowns Too")
        
        self.close_button = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        button_layout_choose = QtWidgets.QHBoxLayout()
        button_layout_choose.addWidget(self.choose_select_attr_button)        
        button_layout_choose.addWidget(self.choose_reduce_attr_button)
        
        fixed_keyframes_layout = QtWidgets.QHBoxLayout()
        fixed_keyframes_layout.addWidget(self.fixed_keyframes_label)
        fixed_keyframes_layout.addWidget(self.fixed_keyframes_edit)
                
        extreme_layout = QtWidgets.QHBoxLayout()
        extreme_layout.addWidget(self.select_extremes_button)        
        extreme_layout.addWidget(self.n_extreme_keyframes_label)
        extreme_layout.addWidget(self.n_extreme_keyframes_slider)
        extreme_layout.addWidget(self.n_extreme_keyframes_edit)
        extreme_button_layout = QtWidgets.QHBoxLayout()
        extreme_button_layout.addWidget(self.extreme_reduce_button)
        
        breakdown_layout = QtWidgets.QHBoxLayout()
        breakdown_layout.addWidget(self.select_breakdowns_button)        
        breakdown_layout.addWidget(self.n_breakdown_keyframes_label)
        breakdown_layout.addWidget(self.n_breakdown_keyframes_slider)
        breakdown_layout.addWidget(self.n_breakdown_keyframes_edit)
        breakdown_button_layout = QtWidgets.QHBoxLayout()
        breakdown_button_layout.addWidget(self.breakdown_reduce_button)
        
        button_layout_bot = QtWidgets.QHBoxLayout()
        button_layout_bot.addWidget(self.close_button)
            
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(button_layout_choose)
        main_layout.addLayout(fixed_keyframes_layout)
        main_layout.addLayout(extreme_layout)
        main_layout.addLayout(extreme_button_layout)
        main_layout.addLayout(breakdown_layout)
        main_layout.addLayout(breakdown_button_layout)
        main_layout.addLayout(button_layout_bot)
        
    def create_connections(self):
        self.choose_select_attr_button.clicked.connect(self.open_choose_for_selection_dialog)
        self.choose_reduce_attr_button.clicked.connect(self.open_choose_for_reduction_dialog)
        self.select_extremes_button.clicked.connect(self.select_extremes)
        self.select_breakdowns_button.clicked.connect(self.select_breakdowns)
        self.extreme_reduce_button.clicked.connect(self.reduce_using_extremes_only)
        self.breakdown_reduce_button.clicked.connect(self.reduce_using_breakdowns_as_well)
        self.n_extreme_keyframes_slider.valueChanged.connect(self.handle_extreme_slider_moved)
        self.n_breakdown_keyframes_slider.valueChanged.connect(self.handle_breakdown_slider_moved)
        self.close_button.clicked.connect(self.close)
    
    def open_choose_for_selection_dialog(self):
        self.select_attr_gui.update_table()
        self.select_attr_gui.show()
        
    def open_choose_for_reduction_dialog(self):
        self.reduce_attr_gui.update_table()
        self.reduce_attr_gui.show()
        
    def read_n_frames(self):
        start = Timeline.get_start()
        end = Timeline.get_end()
        return end - start + 1
         
    def select(self, error_type, fixed_keyframes):
        attr_indices = self.select_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            altmaya.Report.error("You must choose at least one attributes for selection")
            return

        start = altmaya.Timeline.get_start()
        end = altmaya.Timeline.get_end()

        attr_indices = self.select_attr_gui.read_values_as_indices()
        
        data = []
        f = start
        while f <= end:
            data.append(f)
            for ai in attr_indices:
                data.append(ai.read_at_time(f))
            f += 1.0

        n_frames = end - start + 1
        max_keyframes = int(n_frames * 0.2) #int(self.max_keyframes_edit.text())

        if len(fixed_keyframes) > 0:
            max_k = max(fixed_keyframes)
            min_k = min(fixed_keyframes)
            if max_k > end:
                altmaya.Report.error("a fixed keyframe greater than the last frame (fixed=%2.2f, last=%2.2f)" % (max_k, end))
                return
            elif min_k < start:
                altmaya.Report.error("there is a fixed keyframe smaller than the first keyframe (fixed=%2.2f, first=%2.2f)" % (min_k, start))
                return

        fixed_keyframes = [v - start for v in fixed_keyframes]
        result = maya.cmds.salientSelect(error_type, start, end, max_keyframes, fixed_keyframes, data)
        
        selections = {}
        for line in result.split("\n"):
            if line != "":
                errorString, selectionString = line.split("|")
                error = float(errorString)
                selection = [int(v) for v in selectionString.split(",")]
                n_keyframes = len(selection)
                selections[n_keyframes] = { 
                    "selection" : [v + start for v in selection],
                    "error" : error
                }
        
        return selections
        
    def select_extremes(self):
        fixed_keyframes = []
        try:
            fixed_keyframes_str = self.fixed_keyframes_edit.text()
            fixed_keyframes_raw = re.findall("[,\s]?([0-9.]+)[,\s]?", fixed_keyframes_str)
            fixed_keyframes = sorted([float(v) for v in fixed_keyframes_raw])
        except ValueError:
            pass
        self.extreme_selections = self.select("line", fixed_keyframes)
        self.n_extreme_keyframes_slider.setMinimum(min(self.extreme_selections.keys()))
        self.n_extreme_keyframes_slider.setMaximum(max(self.extreme_selections.keys()))
        n = min(self.extreme_selections.keys())
        self.n_extreme_keyframes_slider.setValue(n)
        self.n_extreme_keyframes_edit.setText(str(n))
        selection = self.extreme_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(selection)
        
        
    def select_breakdowns(self):
        n = int(self.n_extreme_keyframes_slider.value())
        fixed_keyframes = sorted(self.extreme_selections[n]["selection"])
        self.breakdown_selections = self.select("curve", fixed_keyframes)
        self.n_breakdown_keyframes_slider.setMinimum(min(self.breakdown_selections.keys()))
        self.n_breakdown_keyframes_slider.setMaximum(max(self.breakdown_selections.keys()))
        n = min(self.breakdown_selections.keys())
        self.n_breakdown_keyframes_slider.setValue(n)
        self.n_breakdown_keyframes_edit.setText(str(n))
        selection = self.breakdown_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(selection)
        
    def handle_extreme_slider_moved(self):
        if len(self.extreme_selections.keys()) == 0:
            altmaya.Report.error("Please run the selection before using this slider")
            return
            
        n = int(self.n_extreme_keyframes_slider.value())
        self.n_extreme_keyframes_edit.setText(str(n))
        
        if n not in self.extreme_selections.keys():
            altmaya.Report.error("No selection of %d keyframes was found?" % n)
            return
            
        selection = self.extreme_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(selection)
        
    def handle_breakdown_slider_moved(self):
        if len(self.breakdown_selections.keys()) == 0:
            altmaya.Report.error("Please run the selection before using this slider")
            return
            
        n = int(self.n_breakdown_keyframes_slider.value())
        self.n_breakdown_keyframes_edit.setText(str(n))
        
        if n not in self.breakdown_selections.keys():
            altmaya.Report.error("No selection of %d keyframes was found?" % n)
            return
            
        selection = self.breakdown_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(selection)
        
    def reduce(self, keyframes):
        """
        Warning: 
            don't shift keyframes to start from zero except for the actual call,
            otherwise this incorrectly offsets the read, cut, and rekeying steps
        """

        attr_indices = self.reduce_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            altmaya.Report.error("You must choose at least one attributes for reduction")
            return
            
        attr_indices = [ v for v in attr_indices if v.has_keyframes() ]
        if len(attr_indices) == 0:
            altmaya.Report.error("No keyframes found on the selected attributes?")
            return
        
        n_keyframes = len(keyframes)
        start = keyframes[0]
        end = keyframes[-1]
        
        altmaya.History.start_undo_block()
        
        try:
                                
            for ai in attr_indices:
                
                data = []
                f = start
                while f <= end:
                    data.append(f)
                    data.append(ai.read_at_time(f))
                    f += 1.0
                    
                result = maya.cmds.salientReduce(
                    ai.obj,
                    ai.attr, 
                    [v - keyframes[0] for v in keyframes], # only 
                    data
                )

                if len(result) % 8 != 0:
                    altmaya.Report.error("Invalid result given by reduction command for %s?" % AttributeIndex(ai.obj, ai.attr))
                    return 
              
                n_cubics = len(result) / 8
                cubics = [Cubic(*result[((i+0)*8):((i+1)*8)]) for i in range(n_cubics)]
                
                # Delete old keyframes
                altmaya.Animation.clear_range(ai, start, end)

                # Set new keyframe values
                for i in range(n_keyframes - 1):
                    altmaya.Animation.add_keyframe(ai, keyframes[i], cubics[i].p1y)
                altmaya.Animation.add_keyframe(ai, keyframes[-1], cubics[-1].p4y)
                
                # Configure keyframes based on fitted cubics
                altmaya.Animation.convert_to_free_splines(ai)
                for i in range(n_cubics):
                    cubic = cubics[i]
                    s = keyframes[i]
                    e = keyframes[i+1]
                    altmaya.Animation.set_keyframe_ingoing_tangent(ai, s, cubic.weightLeft(), cubic.angleLeft() * 180.0 / math.pi)
                    altmaya.Animation.set_keyframe_outgoing_tangent(ai, e, cubic.weightRight(), cubic.angleRight() * 180.0 / math.pi)
        
        except RuntimeError as e:
            altmaya.Report.error("Failed reduce: " + str(e))
            
        altmaya.History.finish_undo_block()
        
    def reduce_using_extremes_only(self):
        n = int(self.n_extreme_keyframes_slider.value())
        keyframes = self.extreme_selections[n]["selection"]
        self.reduce(keyframes)
        
    def reduce_using_breakdowns_as_well(self):
        n = int(self.n_breakdown_keyframes_slider.value())
        keyframes = self.breakdown_selections[n]["selection"]
        self.reduce(keyframes)
        
        
if __name__ == "__main__":    
    try:
        salient_poses_gui.close()
        salient_poses_gui.deleteLater()
    except:
        pass    
        
    salient_poses_gui = SalientPosesGUI()
    salient_poses_gui.show()
    