import math 

from PySide2 import QtCore
from PySide2 import QtWidgets


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


class SalientPosesGUI(StandardMayaWindow):

    def __init__(self):
        super(SalientPosesGUI, self).__init__("Salient Poses")
        
        self.extreme_selections = {}
        self.breakdown_selections = {}
        self.current_selection = []
        self.select_attr_gui = AttributeSelectorForCurrentSelection("Attributes for Selection", [], parent=self)
        self.reduce_attr_gui = AttributeSelectorForCurrentSelection("Attributes for Reduction", [], parent=self)
        
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
        
        self.undo_button = QtWidgets.QPushButton("Undo")
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
        button_layout_bot.addWidget(self.undo_button)
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
        
        self.undo_button.clicked.connect(self.undo_wrapper)
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
            Report.error("You must choose at least one attributes for selection")
            return

        start = Timeline.get_start()
        end = Timeline.get_end()

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
        result = maya.cmds.salientSelect(error_type, start, end, max_keyframes, fixed_keyframes, data)
        
        selections = {}
        for line in result.split("\n"):
            if line != "":
                errorString, selectionString = line.split("|")
                error = float(errorString)
                selection = [int(v) for v in selectionString.split(",")]
                n_keyframes = len(selection)
                selections[n_keyframes] = { "selection" : selection, "error" : error }
        
        return selections
        
    def select_extremes(self):
        fixed_keyframes = []
        try:
            fixed_keyframes_str = self.fixed_keyframes_edit.text()
            fixed_keyframes = [int(v) for v in fixed_keyframes_str.split(",")]
        except ValueError:
            pass
        self.extreme_selections = self.select("line", fixed_keyframes)
        self.n_extreme_keyframes_slider.setMinimum(min(self.extreme_selections.keys()))
        self.n_extreme_keyframes_slider.setMaximum(max(self.extreme_selections.keys()))
        self.n_extreme_keyframes_edit.setText(str(int(self.n_extreme_keyframes_slider.value())))
        
    def select_breakdowns(self):
        n = int(self.n_extreme_keyframes_slider.value())
        fixed_keyframes = self.extreme_selections[n]["selection"]
        self.breakdown_selections = self.select("curve", fixed_keyframes)
        self.n_breakdown_keyframes_slider.setMinimum(min(self.breakdown_selections.keys()))
        self.n_breakdown_keyframes_slider.setMaximum(max(self.breakdown_selections.keys()))
        self.n_breakdown_keyframes_edit.setText(str(int(self.n_breakdown_keyframes_slider.value())))

    def handle_extreme_slider_moved(self):
        if len(self.extreme_selections.keys()) == 0:
            Report.error("Please run the selection before using this slider")
            return
            
        n = int(self.n_extreme_keyframes_slider.value())
        self.n_extreme_keyframes_edit.setText(str(n))
        
        if n not in self.extreme_selections.keys():
            Report.error("No selection of %d keyframes was found?" % n)
            return
            
        selection = self.extreme_selections[n]["selection"]
        Visualize.ghost_keyframes_of_select(selection)
        
    def handle_breakdown_slider_moved(self):
        if len(self.breakdown_selections.keys()) == 0:
            Report.error("Please run the selection before using this slider")
            return
            
        n = int(self.n_breakdown_keyframes_slider.value())
        self.n_breakdown_keyframes_edit.setText(str(n))
        
        if n not in self.breakdown_selections.keys():
            Report.error("No selection of %d keyframes was found?" % n)
            return
            
        selection = self.breakdown_selections[n]["selection"]
        Visualize.ghost_keyframes_of_select(selection)
        
    def reduce(self, keyframes):
        attr_indices = self.reduce_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            Report.error("You must choose at least one attributes for reduction")
            return
            
        attr_indices = [ v for v in attr_indices if v.has_keyframes() ]
        if len(attr_indices) == 0:
            Report.error("No keyframes found on the selected attributes?")
            return
        
        n_keyframes = len(keyframes)
        start = keyframes[0]
        end = keyframes[-1]
        
        History.start_undo_block()
        
        try:
                                
            for ai in attr_indices:
                
                data = []
                f = start
                while f <= end:
                    data.append(f)
                    data.append(maya.cmds.getAttr(ai.key, time=f))
                    f += 1.0
                    
                result = maya.cmds.salientReduce(ai.obj, ai.attr, keyframes, data)
                if len(result) % 8 != 0:
                    Report.error("Invalid result given by reduction command for %s?" % AttributeIndex(ai.obj, ai.attr))
                    return 
              
                n_cubics = len(result) / 8
                cubics = [Cubic(*result[((i+0)*8):((i+1)*8)]) for i in range(n_cubics)]
                
                # Delete old keyframes
                maya.cmds.cutKey(ai.key, time=(start, end))
                
                # Set new keyframe values
                for i in range(n_keyframes - 1):
                    maya.cmds.setKeyframe(ai.key, time=keyframes[i], value=cubics[i].p1y)
                maya.cmds.setKeyframe(ai.key, time=keyframes[-1], value=cubics[-1].p4y)
                
                # Setup splines    
                maya.cmds.keyTangent(ai.key, outTangentType="linear", inTangentType="linear")
                maya.cmds.keyTangent(lock=False)
                maya.cmds.keyTangent(weightedTangents=True)
                maya.cmds.keyTangent(weightLock=False)
                
                # Configure keyframes based on fitted cubics
                for i in range(n_cubics):
                    cubic = cubics[i]
                    s = keyframes[i]
                    e = keyframes[i+1]

                    maya.cmds.keyTangent(
                        ai.key,
                        time=(s, s),
                        edit=True,
                        absolute=True,
                        outWeight=cubic.weightLeft(),
                        outAngle=cubic.angleLeft() * 180.0 / math.pi
                    )

                    maya.cmds.keyTangent(
                        ai.key,
                        time=(e, e),
                        edit=True,
                        absolute=True,
                        inWeight=cubic.weightRight(),
                        inAngle=cubic.angleRight() * 180.0 / math.pi
                    )
        
        except RuntimeError as e:
            Report.error("Failed reduce: " + str(e))
            
        History.finish_undo_block()
        
    def reduce_using_extremes_only(self):
        n = int(self.n_extreme_keyframes_slider.value())
        keyframes = [v + Timeline.get_start() for v in self.extreme_selections[n]["selection"]]
        self.reduce(keyframes)
        
    def reduce_using_breakdowns_as_well(self):
        n = int(self.n_breakdown_keyframes_slider.value())
        keyframes = [v + Timeline.get_start() for v in self.breakdown_selections[n]["selection"]]
        self.reduce(keyframes)
        
    def undo_wrapper(self):
        History.undo()
        
        
if __name__ == "__main__":    
    try:
        salient_poses_gui.close()
        salient_poses_gui.deleteLater()
    except:
        pass    
        
    salient_poses_gui = SalientPosesGUI()
    salient_poses_gui.show()
    