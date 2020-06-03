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


class QtDivider(QtWidgets.QFrame):
    def __init__(self):
        super(QtDivider, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class SalientPosesGUI(altmaya.StandardMayaWindow):

    def __init__(self):
        super(SalientPosesGUI, self).__init__("Salient Poses")
        
        self.fixed_keyframes = []
        self.extreme_selections = {}
        self.breakdown_selections = {}
        self.current_selection = []
        self.extreme_attr_gui = tools.AttributeSelector("Choose Attributes for Selection", [], parent=self)
        self.breakdown_attr_gui = tools.AttributeSelector("Choose Attributes for Selection", [], parent=self)
        self.reduce_attr_gui = tools.AttributeSelector("Choose Attributes for Reduction", [], parent=self)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
        self.lock_extreme_slider()
        self.lock_breakdown_slider()

        self.report_todo("Ready and Waiting")
        
    def create_widgets(self):
        
        # Status bar
        self.status_bar = QtWidgets.QLabel("")
        
        # Fixed keyframes
        self.fixed_keyframes_table = QtWidgets.QTableWidget(0, 3, self)
        self.fixed_keyframes_table.setHorizontalHeaderLabels(['Frame', 'Name', 'Notes'])
        header = self.fixed_keyframes_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.fixed_keyframes_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.fixed_keyframes_button_add_timeline = QtWidgets.QPushButton("Add Min/Max")
        self.fixed_keyframes_button_add_now = QtWidgets.QPushButton("Add Current")
        self.fixed_keyframes_button_add_prompt = QtWidgets.QPushButton("Add (Prompt)")
        self.fixed_keyframes_button_delete = QtWidgets.QPushButton("Delete")
        
        # Extreme section
        self.choose_extreme_attr_button = QtWidgets.QPushButton("Choose Extreme Attributes")
        self.select_extremes_button = QtWidgets.QPushButton("Select Extremes")
        self.n_extreme_keyframes_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.n_extreme_keyframes_edit = QtWidgets.QLineEdit(str(self.n_extreme_keyframes_slider.value()))
        self.n_extreme_keyframes_edit.setEnabled(False)
        self.lock_extremes_button = QtWidgets.QPushButton("Lock Extremes")
        
        # Breakdown section
        self.choose_breakdown_attr_button = QtWidgets.QPushButton("Choose Breakdown Attributes")
        self.select_breakdowns_button = QtWidgets.QPushButton("Select Breakdowns")        
        self.n_breakdown_keyframes_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.n_breakdown_keyframes_edit = QtWidgets.QLineEdit(str(self.n_breakdown_keyframes_slider.value()))
        self.n_breakdown_keyframes_edit.setEnabled(False)
        
        # Reduce section
        self.choose_reduce_attr_button = QtWidgets.QPushButton("Choose Attributes")
        self.extreme_reduce_button = QtWidgets.QPushButton("Reduce (Extremes Only)")
        self.breakdown_reduce_button = QtWidgets.QPushButton("Reduce (Extremes+Breakdowns)")
        
        # Other
        self.close_button = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        main = QtWidgets.QVBoxLayout(self)
        
        # Status bar
        main.addWidget(self.status_bar)
        
        # --------------------------- Divider
        main.addWidget(QtDivider())
        
        main.addWidget(QtWidgets.QLabel("Fixed Keyframes"))
        
        l = QtWidgets.QHBoxLayout()
        l.addWidget(self.fixed_keyframes_table)
        l2 = QtWidgets.QVBoxLayout()
        l2.addWidget(self.fixed_keyframes_button_add_timeline)
        l2.addWidget(self.fixed_keyframes_button_add_now)
        l2.addWidget(self.fixed_keyframes_button_add_prompt)
        l2.addWidget(self.fixed_keyframes_button_delete)
        l.addLayout(l2)
        main.addLayout(l)
        
        # --------------------------- Divider
        main.addWidget(QtDivider())
        
        main.addWidget(QtWidgets.QLabel("Keyframe Selection"))
        
        # Select - extremes
        main.addWidget(self.choose_extreme_attr_button)
        main.addWidget(self.select_extremes_button)
        l = QtWidgets.QHBoxLayout()
        l.addWidget(QtWidgets.QLabel("Extremes"))        
        l.addWidget(self.n_extreme_keyframes_slider)
        l.addWidget(self.n_extreme_keyframes_edit)
        main.addLayout(l)
        
        # Select - lock
        main.addWidget(self.lock_extremes_button)
        
        # Select - breakdowns
        main.addWidget(self.choose_breakdown_attr_button)
        main.addWidget(self.select_breakdowns_button)
        l = QtWidgets.QHBoxLayout()
        l.addWidget(QtWidgets.QLabel("Breakdowns"))
        l.addWidget(self.n_breakdown_keyframes_slider)
        l.addWidget(self.n_breakdown_keyframes_edit)
        main.addLayout(l)
        
        # --------------------------- Divider
        main.addWidget(QtDivider())
        
        main.addWidget(QtWidgets.QLabel("Keyframe Reduction"))
        
        # Reduce
        l = QtWidgets.QHBoxLayout()
        l.addWidget(self.choose_reduce_attr_button)
        l.addWidget(self.extreme_reduce_button)
        l.addWidget(self.breakdown_reduce_button)
        main.addLayout(l)
        
        # --------------------------- Divider
        main.addWidget(QtDivider())
        
        # Other
        l = QtWidgets.QHBoxLayout()
        l.addWidget(self.close_button)
        main.addLayout(l)
            
        
    def create_connections(self):
        
        # Setup section
        self.fixed_keyframes_button_add_timeline.clicked.connect(self.add_fiexed_via_timeline)
        self.fixed_keyframes_button_add_now.clicked.connect(self.add_fixed_via_current)
        self.fixed_keyframes_button_add_prompt.clicked.connect(self.add_fixed_via_prompt)
        self.fixed_keyframes_button_delete.clicked.connect(self.deleted_fixed)
        
        # Select section
        self.choose_extreme_attr_button.clicked.connect(self.open_choose_for_extreme_dialog)
        self.select_extremes_button.clicked.connect(self.select_extremes)
        self.lock_extremes_button.clicked.connect(self.lock_extremes)
        self.choose_breakdown_attr_button.clicked.connect(self.open_choose_for_breakdown_dialog)
        self.select_breakdowns_button.clicked.connect(self.select_breakdowns)
        self.n_extreme_keyframes_slider.valueChanged.connect(self.handle_extreme_slider_moved)
        self.n_breakdown_keyframes_slider.valueChanged.connect(self.handle_breakdown_slider_moved)
        
        # Reduce section
        self.choose_reduce_attr_button.clicked.connect(self.open_choose_for_reduction_dialog)
        self.extreme_reduce_button.clicked.connect(self.reduce_using_extremes_only)
        self.breakdown_reduce_button.clicked.connect(self.reduce_using_breakdowns_as_well)
        
        # Other
        self.close_button.clicked.connect(self.close)

    def set_status(self, message, color_as_hex):
        font_hex = "%02x%02x%02x" % (55, 55, 55)
        self.status_bar.setText("> " + message)
        self.status_bar.setStyleSheet("background: #%s; color: #%s" % (color_as_hex, font_hex))
        
    def report_error(self, message):
        self.set_status(message, "F20505")
        altmaya.Report.error(message)
        
    def report_warning(self, message):
        self.set_status(message, "F2BE22")
        altmaya.Report.warning(message)

    def report_todo(self, message):
        self.set_status(message, "F2BE22")
        altmaya.Report.message(message)
        
    def report_message(self, message):
        self.set_status(message, "446644")
        altmaya.Report.message(message)
    
    def open_choose_for_extreme_dialog(self):
        self.extreme_attr_gui.update_table()
        self.extreme_attr_gui.show()
        
    def open_choose_for_breakdown_dialog(self):
        self.breakdown_attr_gui.update_table()
        self.breakdown_attr_gui.show()
        
    def open_choose_for_reduction_dialog(self):
        self.reduce_attr_gui.update_table()
        self.reduce_attr_gui.show()
        
    def update_table(self):
        self.fixed_keyframes_table.setRowCount(len(self.fixed_keyframes))
        for (i, (frame, name, notes)) in enumerate(self.fixed_keyframes):
            
            # For frame number
            item = QtWidgets.QTableWidgetItem()
            item.setText(str(frame))
            self.fixed_keyframes_table.setItem(i, 0, item)
            
            # For name
            item = QtWidgets.QTableWidgetItem()
            item.setText(name)
            self.fixed_keyframes_table.setItem(i, 1, item)
            
            # For notes
            item = QtWidgets.QTableWidgetItem()
            item.setText(notes)
            self.fixed_keyframes_table.setItem(i, 2, item)

    def add_fixed_at(self, frame, name="", notes=""):
        fixed_frames = [v[0] for v in self.fixed_keyframes]
        if frame in fixed_frames:
            self.report_error("%s is already in fixed keyframes" % frame)
            return
        self.fixed_keyframes.append((frame, name, notes))
        self.fixed_keyframes = sorted(self.fixed_keyframes, key=lambda t: t[0])
        
        self.update_table()
        self.lock_extreme_slider()
        self.lock_breakdown_slider()
        self.report_message("Added fixed keyframe at %d" % frame)
        
    def add_fiexed_via_timeline(self):
        self.add_fixed_at(int(altmaya.Timeline.get_start()), name="Min")
        self.add_fixed_at(int(altmaya.Timeline.get_end()), name="Max")
        
    def add_fixed_via_current(self):
        frame = int(altmaya.Timeline.get_current_frame())
        self.add_fixed_at(frame)
        
    def add_fixed_via_prompt(self):
        fixed_str = altmaya.Ask.string(self, "Add fixed keyframe", "Enter fixed keyframes, separated by commas or spaces", "1, 2, 3")
        raw = re.findall("[,\s]?([0-9.]+)[,\s]?", fixed_str)
        for v in raw:
            frame = int(v)
            self.add_fixed_at(frame)
        
    def deleted_fixed(self):
        sel = self.fixed_keyframes_table.selectionModel().selectedRows(0)
        for s in sel:            
            r = s.row()
            frame = int(self.fixed_keyframes_table.item(r, 0).text())
            name = self.fixed_keyframes_table.item(r, 1).text()
            notes = self.fixed_keyframes_table.item(r, 2).text()
            self.fixed_keyframes.remove((frame, name, notes))
        self.fixed_keyframes = sorted(self.fixed_keyframes, key=lambda t: t[0])
        
        self.update_table()
        self.lock_extreme_slider()
        self.lock_breakdown_slider()
        self.report_message("Deleted fixed keyframes")
        
    def lock_extreme_slider(self):
        self.n_extreme_keyframes_slider.setEnabled(False)
        # self.n_extreme_keyframes_edit.setEnabled(False)
        
        
    def lock_breakdown_slider(self):
        self.n_breakdown_keyframes_slider.setEnabled(False)
        # self.n_breakdown_keyframes_edit.setEnabled(False)
        
        
    def unlock_extreme_slider(self):
        self.n_extreme_keyframes_slider.setEnabled(True)
        # self.n_extreme_keyframes_edit.setEnabled(True)
        
        
    def unlock_breakdown_slider(self):
        self.n_breakdown_keyframes_slider.setEnabled(True)
        # self.n_breakdown_keyframes_edit.setEnabled(True)
        
         
    def select(self, attr_indices, error_type, fixed_keyframes):
        start = fixed_keyframes[0]
        end = fixed_keyframes[-1]
        
        data = []
        f = start
        while f <= end:
            data.append(f)
            for ai in attr_indices:
                data.append(ai.read_at_time(f))
            f += 1.0

        n_frames = end - start + 1
        max_keyframes = int(n_frames * 0.2) #int(self.max_keyframes_edit.text())
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
        attr_indices = self.extreme_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            self.report_error("You must choose at least one attributes for selection")
            return
            
        ret = self.select(attr_indices, "line", [v[0] for v in self.fixed_keyframes])
        if ret is None: self.report_error("Something went very wrong! Please post an issue at https://github.com/richard-roberts/SalientPosesMaya/issues")
        
        self.extreme_selections = ret
        self.n_extreme_keyframes_slider.setMinimum(min(self.extreme_selections.keys()))
        self.n_extreme_keyframes_slider.setMaximum(max(self.extreme_selections.keys()))
        n = min(self.extreme_selections.keys())
        self.n_extreme_keyframes_slider.setValue(n)
        self.n_extreme_keyframes_edit.setText(str(n))
        selection = self.extreme_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(selection)
        
        self.unlock_extreme_slider()
        self.report_message("Finished selecting extremes!")
        
    def select_breakdowns(self):
        attr_indices = self.breakdown_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            self.report_error("You must choose at least one attributes for selection")
            return    
        n_e = int(self.n_extreme_keyframes_slider.value())
        extremes = sorted(self.extreme_selections[n_e]["selection"])
        
        ret = self.select(attr_indices, "curve", extremes)
        if ret is None: self.report_error("Something went very wrong! Please post an issue at https://github.com/richard-roberts/SalientPosesMaya/issues")
        
        self.breakdown_selections = ret
        n = min(self.breakdown_selections.keys())
        
        self.n_breakdown_keyframes_slider.setMinimum(min(self.breakdown_selections.keys()) - n_e)
        self.n_breakdown_keyframes_slider.setMaximum(max(self.breakdown_selections.keys()) - n_e)
        self.n_breakdown_keyframes_slider.setValue(n - n_e)
        self.n_breakdown_keyframes_edit.setText(str(n - n_e))        
        selection = self.breakdown_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(selection)
        
        self.unlock_breakdown_slider()
        self.report_message("Finished selecting breakdowns!")
        
    def lock_extremes(self):
        if self.n_extreme_keyframes_slider.isEnabled():
            self.lock_extreme_slider()
            self.report_message("Locked extreme selection")
            if altmaya.Ask.decision(
                self,
                "Duplicate extreme poses",
                "Would you like to duplicate extreme poses for the selected object?"
            ):
                altmaya.Animation.clear_ghosts()
                sel = altmaya.Selection.get()
                n = int(self.n_extreme_keyframes_slider.value())
                keyframes = sorted(self.extreme_selections[n]["selection"])
                for (ix, k) in enumerate(keyframes):
                    altmaya.Timeline.set_current_frame(k)
                    for s in sel:
                        name = name="%s_extreme%d" % (s, ix)
                        altmaya.Functions.duplicate(s, name=name)
                altmaya.Selection.set(sel)
                    
        else:
            self.unlock_extreme_slider()
            self.report_message("Unlocked extremes selection")
        
    def handle_extreme_slider_moved(self):
        if len(self.extreme_selections.keys()) == 0:
            self.report_error("Please run the extreme selection before using this slider")
            return
            
        n = int(self.n_extreme_keyframes_slider.value())
        self.n_extreme_keyframes_edit.setText(str(n))
        
        if n not in self.extreme_selections.keys():
            self.report_error("No selection of %d keyframes was found?" % n)
            return
            
        selection = self.extreme_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(selection)
        
    def handle_breakdown_slider_moved(self):
        if len(self.breakdown_selections.keys()) == 0:
            self.report_error("Please run the breakdowm selection before using this slider")
            return
         
        n_e = int(self.n_extreme_keyframes_slider.value())   
        n_b = int(self.n_breakdown_keyframes_slider.value())
        self.n_breakdown_keyframes_edit.setText(str(n_b))
        
        n = n_e + n_b
        if n not in self.breakdown_selections.keys():
            self.report_error("No selection of %d keyframes was found?" % n)
            return
        
        extremes = self.extreme_selections[n_e]["selection"]    
        selection = self.breakdown_selections[n]["selection"]
        altmaya.Animation.ghost_keyframes(
            [k for k in selection if k not in extremes]
        )
        
    def reduce(self, keyframes, breakdowns):
        """
        Warning: 
            don't shift keyframes to start from zero except for the actual call,
            otherwise this incorrectly offsets the read, cut, and rekeying steps
        """

        attr_indices = self.reduce_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            self.report_error("You must choose at least one attributes for reduction")
            return
            
        attr_indices = [ v for v in attr_indices if v.has_keyframes() ]
        if len(attr_indices) == 0:
            self.report_error("No keyframes found on the selected attributes?")
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
                    self.report_error("Invalid result given by reduction command for %s?" % AttributeIndex(ai.obj, ai.attr))
                    return 
              
                n_cubics = len(result) / 8
                cubics = [Cubic(*result[((i+0)*8):((i+1)*8)]) for i in range(n_cubics)]
                
                # Delete old keyframes
                altmaya.Animation.clear_range(ai, start, end)

                # Set new keyframe values
                for i in range(n_keyframes - 1):
                    is_breakdown = keyframes[i] not in breakdowns
                    altmaya.Animation.add_keyframe(ai, keyframes[i], cubics[i].p1y, is_breakdown)
                altmaya.Animation.add_keyframe(ai, keyframes[-1], cubics[-1].p4y, False)
                
                # Configure keyframes based on fitted cubics
                altmaya.Animation.convert_to_free_splines(ai)
                for i in range(n_cubics):
                    cubic = cubics[i]
                    s = keyframes[i]
                    e = keyframes[i+1]
                    altmaya.Animation.set_keyframe_ingoing_tangent(ai, s, cubic.weightLeft(), cubic.angleLeft() * 180.0 / math.pi)
                    altmaya.Animation.set_keyframe_outgoing_tangent(ai, e, cubic.weightRight(), cubic.angleRight() * 180.0 / math.pi)
        
        except RuntimeError as e:
            self.report_error("Failed reduce: " + str(e))
            
        altmaya.History.finish_undo_block()
        
    def reduce_using_extremes_only(self):
        n = int(self.n_extreme_keyframes_slider.value())
        if n not in self.extreme_selections.keys():
            self.report_error("No extreme keyframes found for n=%d, did you run extreme selection?" % n)
            return
        keyframes = self.extreme_selections[n]["selection"]
        self.reduce(keyframes)
        
    def reduce_using_breakdowns_as_well(self):
        n_e = int(self.n_extreme_keyframes_slider.value())
        n_b = int(self.n_breakdown_keyframes_slider.value())
        n = n_e + n_b
        if n not in self.breakdown_selections.keys():
            self.report_error("No breakdown keyframes found for n=%d, did you run breakdown selection?" % n)
            return
        extremes = self.extreme_selections[n_e]["selection"]
        keyframes = self.breakdown_selections[n]["selection"]
        breakdowns = [v for v in keyframes if v not in extremes]
        self.reduce(keyframes, breakdowns)
        
        
if __name__ == "__main__":    
    try:
        salient_poses_gui.close()
        salient_poses_gui.deleteLater()
    except:
        pass    
        
    salient_poses_gui = SalientPosesGUI()
    salient_poses_gui.show()
    