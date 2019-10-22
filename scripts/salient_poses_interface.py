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
        
        self.selections = {}
        self.select_attr_gui = AttributeSelectorForCurrentSelection("Attributes for Selection", [])
        self.reduce_attr_gui = AttributeSelectorForCurrentSelection("Attributes for Reduction", [])
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.choose_select_attr_button = QtWidgets.QPushButton("Choose")
        self.choose_reduce_attr_button = QtWidgets.QPushButton("Choose")
        
        self.select_button = QtWidgets.QPushButton("Select")
        self.reduce_button = QtWidgets.QPushButton("Reduce")
        self.undo_button = QtWidgets.QPushButton("Undo")
        
        self.n_frames_label = QtWidgets.QLabel("Number of Frames")
        self.n_frames_edit = QtWidgets.QLineEdit(str(self.read_n_frames()))
        self.n_frames_edit.setEnabled(False)
        
        self.max_keyframes_label = QtWidgets.QLabel("Maximum Keyframes")
        self.max_keyframes_edit = QtWidgets.QLineEdit(str(int(self.read_n_frames() * 0.2)))
        self.max_keyframes_edit.setEnabled(False)
        
        self.n_keyframes_label = QtWidgets.QLabel("N Keyframes")
        self.n_keyframes_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.n_keyframes_edit = QtWidgets.QLineEdit(str(self.n_keyframes_slider.value()))
        self.n_keyframes_edit.setEnabled(False)
        
        self.close_button = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        button_layout_choose = QtWidgets.QHBoxLayout()
        button_layout_choose.addWidget(self.choose_select_attr_button)
        button_layout_choose.addWidget(self.choose_reduce_attr_button)
                
        button_layout_select = QtWidgets.QHBoxLayout()
        button_layout_select.addWidget(self.select_button)        
        
        keyframes_layout_n_frames = QtWidgets.QHBoxLayout()
        keyframes_layout_n_frames.addWidget(self.n_frames_label)
        keyframes_layout_n_frames.addWidget(self.n_frames_edit)
        
        keyframes_layout_max_keyframes = QtWidgets.QHBoxLayout()
        keyframes_layout_max_keyframes.addWidget(self.max_keyframes_label)
        keyframes_layout_max_keyframes.addWidget(self.max_keyframes_edit)
        
        keyframes_layout_n_keyframes = QtWidgets.QHBoxLayout()
        keyframes_layout_n_keyframes.addWidget(self.n_keyframes_label)
        keyframes_layout_n_keyframes.addWidget(self.n_keyframes_slider)
        keyframes_layout_n_keyframes.addWidget(self.n_keyframes_edit)
        
        button_layout_reduce = QtWidgets.QHBoxLayout()
        button_layout_reduce.addWidget(self.reduce_button)
        button_layout_reduce.addWidget(self.undo_button)
        
        button_layout_bot = QtWidgets.QHBoxLayout()
        button_layout_bot.addWidget(self.close_button)
            
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(button_layout_choose)
        main_layout.addLayout(button_layout_select)
        main_layout.addLayout(keyframes_layout_n_frames)
        main_layout.addLayout(keyframes_layout_max_keyframes)
        main_layout.addLayout(keyframes_layout_n_keyframes)
        main_layout.addLayout(button_layout_reduce)
        main_layout.addLayout(button_layout_bot)
        
    def create_connections(self):
        self.choose_select_attr_button.clicked.connect(self.open_choose_for_selection_dialog)
        self.choose_reduce_attr_button.clicked.connect(self.open_choose_for_reduction_dialog)
        self.select_button.clicked.connect(self.select)
        self.reduce_button.clicked.connect(self.reduce)
        self.undo_button.clicked.connect(self.undo_wrapper)
        self.n_keyframes_slider.valueChanged.connect(self.handle_slider_moved)
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
         
    def select(self):
        attr_indices = self.select_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            Report.error("You must choose at least one attributes for selection")
            return
        
        History.start_undo_block()
        
        try:
        
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

            max_keyframes = int(self.max_keyframes_edit.text())
            result = maya.cmds.salientSelect(start, end, max_keyframes, data)
            
            self.selections = {}
            for line in result.split("\n"):
                if line != "":
                    errorString, selectionString = line.split("|")
                    error = float(errorString)
                    selection = [int(v) for v in selectionString.split(",")]
                    n_keyframes = len(selection)
                    self.selections[n_keyframes] = { "selection" : selection, "error" : error }
              
            self.n_keyframes_slider.setMinimum(min(self.selections.keys()))
            self.n_keyframes_slider.setMaximum(max(self.selections.keys()))
            self.n_keyframes_edit.setText(str(int(self.n_keyframes_slider.value())))
            
        except RuntimeError as e:
            Report.error("Failed select: " + str(e))
        
        History.finish_undo_block()
        
    def reduce(self):
        attr_indices = self.reduce_attr_gui.read_values_as_indices()
        if len(attr_indices) == 0:
            Report.error("You must choose at least one attributes for reduction")
            return
            
        attr_indices = [ v for v in attr_indices if v.has_keyframes() ]
        if len(attr_indices) == 0:
            Report.error("No keyframes found on the selected attributes?")
            return
        
        n = int(self.n_keyframes_slider.value())
        if n not in self.selections.keys():
            Report.error("No selection of `%d` keyframes found for reduction?" % n)
            return
            
        keyframes = [v + Timeline.get_start() for v in self.selections[n]["selection"]]
        n_keyframes = len(keyframes)
        start = keyframes[0]
        end = keyframes[-1]
        
        History.start_undo_block()
        
        try:
                                
            for ai in attr_indices:
                result = maya.cmds.salientReduce(ai.obj, ai.attr, keyframes)
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
        
    def undo_wrapper(self):
        History.undo()

    def handle_slider_moved(self):
        if len(self.selections.keys()) == 0:
            Report.error("Please run the selection before using this slider")
            return
            
        n = int(self.n_keyframes_slider.value())
        self.n_keyframes_edit.setText(str(n))
        
        if n not in self.selections.keys():
            Report.error("No selection of %d keyframes was found?" % n)
            return
            
        selection = self.selections[n]["selection"]
        Visualize.ghost_keyframes_of_select(selection)
        
        
if __name__ == "__main__":    
    try:
        salient_poses_gui.close()
        salient_poses_gui.deleteLater()
    except:
        pass    
        
    salient_poses_gui = SalientPosesGUI()
    salient_poses_gui.show()
    