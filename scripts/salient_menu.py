import math

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import QPen, QBrush, QPainter
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui 
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin


WINDOW_WIDTH = 400
WINDOW_QUARTER = WINDOW_WIDTH * 0.25
LABEL_WIDTH = WINDOW_QUARTER * 1


class Prompt:

    @staticmethod
    def get_file(message):
        paths = cmds.fileDialog2(fileMode=0, caption=message)
        if paths == None:
            cmds.error("Please select a valid filepath")
            return None
        elif len(paths) == 1:
            return paths[0]
        else:
            cmds.error("Please select a valid filepath")
            return None

    @staticmethod
    def get_folder(message):
        paths = cmds.fileDialog2(fileMode=2, caption=message)
        if paths == None:
            cmds.error("Please select a valid filepath")
        elif len(paths) == 1:
            return paths[0]
        else:
            cmds.error("Please select a valid filepath")
            return None
    
    @staticmethod
    def get_string(title, message):
        result = cmds.promptDialog(
                    title=title,
                    message=message,
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

        if result == 'OK':
            return cmds.promptDialog(query=True, text=True)
        else:
            return None

class UIFonts:
    header = QtGui.QFont("Arial", 10, QtGui.QFont.Bold)

class UIBuilder:

    @staticmethod
    def vertical_box(parent=None, add_to=None):
        vbox = QtWidgets.QVBoxLayout(parent)
        if add_to != None: add_to.addLayout(vbox)
        return vbox

    @staticmethod
    def horizontal_box(parent=None, add_to=None):
        hbox = QtWidgets.QHBoxLayout(parent)
        if add_to != None: add_to.addLayout(hbox)
        return hbox

    @staticmethod
    def make_separator(add_to):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        add_to.addWidget(line)

    @staticmethod
    def make_spacer(add_to, size):
        spacer = QtWidgets.QSpacerItem(size[0], size[1])
        add_to.addItem(spacer)

    @staticmethod
    def make_spacer_1(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 1, 10))

    @staticmethod
    def make_spacer_2(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 2, 10))

    @staticmethod
    def make_spacer_3(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 3, 10))

    @staticmethod
    def make_spacer_4(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 4, 10))

    @staticmethod
    def label(add_to, text, size=-1, font=None):
        label = QtWidgets.QLabel(text)
        label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        label.setMinimumWidth(LABEL_WIDTH if size == -1 else size)
        label.setMaximumWidth(LABEL_WIDTH if size == -1 else size)
        if font is not None: label.setFont(font)
        add_to.addWidget(label)
        return label

    @staticmethod
    def button(add_to, text, fn=None):
        button = QtWidgets.QPushButton(text)
        button.setMinimumWidth(WINDOW_QUARTER)
        button.setMaximumWidth(WINDOW_QUARTER)
        button.setText(text)
        if fn != None: button.pressed.connect(fn)
        add_to.addWidget(button)
        return button

    @staticmethod
    def check_box(add_to, fn=None, starts=False):
        check_box = QtWidgets.QCheckBox()
        if starts:
            check_box.setCheckState(QtCore.Qt.CheckState(True))
        else:
            check_box.setCheckState(QtCore.Qt.CheckState(False))

        if fn != None: check_box.stateChanged.connect(fn)
        add_to.addWidget(check_box)
        return check_box

    @staticmethod
    def line_edit(add_to, text, fn=None):
        line_edit = QtWidgets.QLineEdit()
        line_edit.setText(text)
        if fn != None: line_edit.returnPressed.connect(fn)
        add_to.addWidget(line_edit)
        return line_edit

    @staticmethod
    def slider(add_to, min_v, max_v, step_size, value, fn=None):
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setSingleStep(step_size)
        slider.setRange(min_v, max_v)
        slider.setValue(value)
        if fn != None: slider.valueChanged.connect(fn)
        add_to.addWidget(slider)
        return slider

    @staticmethod
    def make_combo(add_to, items, fn=None):
        combo = QtWidgets.QComboBox()
        for item in items: combo.addItem(item)
        if fn != None: combo.currentIndexChanged.connect(fn)
        add_to.addWidget(combo)
        return combo

    @staticmethod
    def list(add_to, items, fn=None):
        qlist = QtWidgets.QListWidget()
        for item in items: qlist.addItem(item)
        if fn != None: qlist.itemSelectionChanged.connect(fn)
        add_to.addWidget(qlist)    
        return qlist

class UIHelper:

    @staticmethod
    def set_active_index(list_object, index):
        return list_object.setCurrentRow(index)

    @staticmethod
    def current_item_not_none(list_object):
        return list_object.currentItem() is not None

    @staticmethod
    def read_active_item_from_list(list_object):
        return list_object.currentItem().data(32)

    @staticmethod
    def read_items_from_list(list_object):
        return [list_object.item(i).data(32) for i in range(list_object.count())]

    @staticmethod
    def pop_active_item_from_list(list_object):
        return list_object.takeItem(list_object.currentRow()).data(32)

    @staticmethod
    def add_item_to_list(name, item, list_object):
        list_item = QtWidgets.QListWidgetItem()
        list_item.setText(name)
        list_item.setData(32, item)
        list_object.addItem(list_item)
        list_object.setCurrentItem(list_item)

    @staticmethod
    def add_items_to_list(names, items, list_object):
        for (name, item) in zip(names, items):
            UIHelper.add_item_to_list(name, item, list_object)

    @staticmethod
    def clear_list(list_object):
        list_object.clear()

class DrawingBuilder:

    @staticmethod
    def makeRGBColor(r, g, b):
        return QtGui.QColor.fromRgb(r, g, b)

    @staticmethod
    def makeHSLColor(h, s, v):
        return QtGui.QColor.fromHsvF(h / 360.0, s / 100.0, v / 100.0)

    @staticmethod
    def red():
        return DrawingBuilder.makeHSLColor(6, 75, 70)
    
    @staticmethod
    def blue():
        return DrawingBuilder.makeHSLColor(182, 29, 81)
    
    @staticmethod
    def white():
        return DrawingBuilder.makeHSLColor(233, 4, 91)

    @staticmethod
    def create_background_color_fn(r, g, b):
        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            brush = QBrush(QtGui.QColor.fromRgb(r, g, b))
            pen = QPen(QtGui.QColor.fromRgb(0, 0, 0, a=0))
            painter.setBrush(brush)
            painter.setPen(pen)
            painter.drawRect(0, 0, w, h)
        return fn

    @staticmethod
    def create_points_fn(points, color, size=1):
        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            pen = QPen(color, size)
            painter.setPen(pen)
            for (a, b) in zip(points[:-1], points[1:]):
                painter.drawLine(a[0] * w, h - a[1] * h, b[0] * w, h - b[1] * h)
        return fn
    
    @staticmethod
    def create_horizontal_line_based_on_attribute_fn(get_attr_fn, get_attr_range_fn, color, size=1):

        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            pen = QPen(color, size)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)    
            min_v, max_v = get_attr_range_fn()
            y = h * (1 - ((get_attr_fn() - min_v) / (max_v - min_v)))
            painter.drawLine(0, y, w, y)
        return fn

    @staticmethod
    def create_vertical_line_based_on_attribute_fn(get_attr_fn, get_attr_range_fn, color, size=1):
        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            pen = QPen(color, size)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            min_v, max_v = get_attr_range_fn()
            x = w * (get_attr_fn() - min_v) / (max_v - min_v)
            painter.drawLine(x, 0, x, h)
        return fn

    @staticmethod
    def make(add_to, parent, size):

        class DrawingWidget(QtWidgets.QWidget):

            def __init__(self):
                super(DrawingWidget, self).__init__()
                self.setParent(parent)
                self.resize(size[0], size[1])
                self.enabledState = False
                self.enabled = True

                self.disabled_fn = DrawingBuilder.create_background_color_fn(50, 50, 50)
                self.drawing_fns = [DrawingBuilder.create_background_color_fn(30, 30, 30)]

                vbox = UIBuilder.vertical_box(parent=self)
                UIBuilder.make_spacer(vbox, size)

            def reset_drawing_fns(self):
                self.drawing_fns = [DrawingBuilder.create_background_color_fn(30, 30, 30)]
                self.enabledState = False

            def add_drawing_fn(self, fn):
                self.drawing_fns.append(fn)

            def activate(self):
                self.enabledState = True

            def paintEvent(self, e):
                painter = QPainter(self)
                if not self.enabledState:
                    self.disabled_fn(self, painter)
                else:
                    for fn in self.drawing_fns:
                        fn(self, painter)

        painter = DrawingWidget()
        add_to.addWidget(painter)
        return painter

class SavedAnimation:

    def __init__(self, objects, start, end):
        self.objects = objects
        self.start = start
        self.end = end

        self.save()

    def save(self):
        self.animation = {}
        for object in self.objects:
            data = {}
            connections = cmds.listConnections(object)
            if connections is None:
                return

            curves = [x for x in connections if "animCurve" in cmds.nodeType(x)]
            for curve in curves:
                
                times = cmds.keyframe(curve, query=True, time=(self.start, self.end))
                if times is None:
                    data[curve] = None
                else:                    
                    values = [cmds.keyframe(curve, time=(t, t), eval=True, query=True)[0] for t in times]
                    inWeights = [cmds.keyTangent(curve, query=True, time=(t, t), inWeight=True)[0] for t in times]
                    inAngles = [cmds.keyTangent(curve, query=True, time=(t, t), inAngle=True)[0] for t in times]
                    outWeights = [cmds.keyTangent(curve, query=True, time=(t, t), outWeight=True)[0] for t in times]
                    outAngles = [cmds.keyTangent(curve, query=True, time=(t, t), outAngle=True)[0] for t in times]

                    data[curve] = {
                        "keys" : list(zip(times, values)),
                        "ins" : list(zip(inWeights, inAngles)),
                        "outs" : list(zip(outWeights, outAngles))
                    }

            self.animation[object] = data

    def revert(self):
        for object in self.animation.keys():
            data = self.animation[object]
            curves = data.keys()
            for curve in curves:

                # Curve contained no keyframe data when saved, so cut whatever is there now
                if data[curve] == None:
                    cmds.cutKey(curve, time=(self.start, self.end))
                    return

                keys = data[curve]["keys"]
                times = [k[0] for k in keys]
                ins = data[curve]["ins"]
                outs = data[curve]["outs"]
                curve_data = list(zip(keys, ins, outs))

                start = times[0]
                end = times[-1]

                # Remove all frames in section
                for (s, e) in zip(times[:-1], times[1:]):
                    if e - s > 1:
                        cmds.cutKey(curve, time=(s + 1, e - 1))

                # Rebuild the animation
                for ((time, value), (inWeight, inAngle), (outWeight, outAngle)) in curve_data:
                    cmds.setKeyframe(curve, value=value, time=time)
                    cmds.keyTangent(curve, edit=True, time=(time, time), inWeight=inWeight, inAngle=inAngle, absolute=True)
                    cmds.keyTangent(curve, edit=True, time=(time, time), outWeight=outWeight, outAngle=outAngle, absolute=True)

class SalientPoses:

    @staticmethod
    def get_dimensions():
        dimensions = ["time"]
        for object in cmds.ls(selection=True):
            dimensions += ["%s.%s" % (object, attr) for attr in ["tx", "ty", "tz"]]
        return dimensions
    
    @staticmethod
    def get_animation_data(start, end):
        sel = cmds.ls(selection=True)

        # Attach proxies
        proxies = []
        for object in sel:
            proxy = cmds.spaceLocator()[0]
            cmds.parentConstraint(object, proxy)
            proxies.append(proxy)

        # Get world-space position of proxies
        anim_data = []
        for i in range(start, end + 1):
            anim_data += [float(i)]
            for object in proxies:
                anim_data += cmds.getAttr("%s.worldMatrix" % object, time=i)[12:15]
        
        # Clean up
        cmds.delete(proxies)
        cmds.select(sel, replace=True)
        return anim_data

def select_keyframes(cl_platform_ix, cl_device_ix, start, end, fixed_keyframes):
    anim_data = SalientPoses.get_animation_data(start, end)
    dimensions = SalientPoses.get_dimensions()

    # Select
    result = cmds.salientSelect(
        cl_platform_ix, cl_device_ix,
        start, end,
        anim_data, dimensions, fixed_keyframes
    )
    
    # Compile selections from result
    selections = {}
    for line in result.split("\n"):
        if line != "":
            errorString, selectionString = line.split("|")
            error = float(errorString)
            selection = [int(v) for v in selectionString.split(",")]
            n_keyframes = len(selection)
            selections[n_keyframes] = { "selection" : selection, "error" : error }
    return selections

def reduce_keyframes(selection):
    start = selection[0]
    end = selection[-1]

    # Bake
    objects = cmds.ls(selection=True)
    cmds.bakeResults(objects, t=(start, end), sampleBy=1, minimizeRotation=True, preserveOutsideKeys=True)

    # Reduce
    cmds.salientReduce(start=start, finish=end, selection=selection)

def getMayaMainWindow():
    mayaPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaPtr), QtWidgets.QWidget)
    
_win = None
def show():
    global _win
    _win = SalientPosesDialog(parent=getMayaMainWindow())
    _win.show(dockable=True)

class SalientPosesDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(SalientPosesDialog, self).__init__(parent)
        self.my_parent = parent
        
        self.selections = {}
        self.saved_animations = []

        def init_ui(): 
            vbox = UIBuilder.vertical_box(parent=self)

            # OpenCL device choice
            listed_devices = [v for v in cmds.salientOpenCLInfo().split("\n") if v != ""]
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "OpenCL Device")
            self.opencl_device_combo = UIBuilder.make_combo(hbox, listed_devices)
            
            # Fixed keyframes text field
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Fixed Keyframes")
            self.fixed_keyframes_edit = UIBuilder.line_edit(hbox, "")

            # N keyframes text field
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "N Keyframes")
            self.n_keyframes_edit = UIBuilder.line_edit(hbox, str(3), self.set_n_keyframes_via_text)

            # Error text field
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Error")
            self.error_edit = UIBuilder.line_edit(hbox, "%2.4f" % -1)
            self.error_edit.setEnabled(False)

            # N keyframes slider
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            start = int(cmds.playbackOptions(query=True, minTime=True))
            end = int(cmds.playbackOptions(query=True, maxTime=True))
            self.n_keyframes_slider = UIBuilder.slider(hbox, 3, end - start + 1, 1, 3, self.set_n_keyframes_via_slider)

            # Error drawing
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            self.painter = DrawingBuilder.make(hbox, self, (200, 200))

            # Actions
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Actions")
            UIBuilder.button(hbox, "Evaluate", fn=self.do_select)
            UIBuilder.button(hbox, "Reduce", fn=self.do_reduce)
            self.undo_button = UIBuilder.button(hbox, "Undo (0)", fn=self.revert_to_saved)

        init_ui()
        self.setWindowTitle('Salient Poses')

    def save_animation(self, objects, start, end):
        saved = SavedAnimation(objects, start, end)
        self.saved_animations.append(saved)
        self.undo_button.setText("Undo (%d)" % len(self.saved_animations))

    def revert_to_saved(self):
        if len(self.saved_animations) > 0:
            self.saved_animations.pop().revert()
            self.undo_button.setText("Undo (%d)" % len(self.saved_animations))
        else:
            cmds.error("No more animations left in undo history")

    def do_select(self):
        opencl_device_info_str = self.opencl_device_combo.currentText()
        cl_platform_ix_str, cl_device_ix_str = opencl_device_info_str.split(" ")[0].split(".")
        cl_platform_ix = int(cl_platform_ix_str)
        cl_device_ix = int(cl_device_ix_str)

        fixed_keyframes = []
        fixed_keyframes_text = self.fixed_keyframes_edit.text().strip()
        if fixed_keyframes_text != "":
            fixed_keyframes = [int(v) for v in self.fixed_keyframes_edit.text().split(",")]

        start = int(cmds.playbackOptions(query=True, minTime=True))
        end = int(cmds.playbackOptions(query=True, maxTime=True))
        self.selections = select_keyframes(cl_platform_ix, cl_device_ix, start, end, fixed_keyframes)

        # Update slider bounds
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())

        self.update_visualization()

    def do_reduce(self):
        objects = cmds.ls(selection=True)

        # Convert all animation curves to independent euler
        command_str = "rotationInterpolation -c none"
        for object in objects:
            command_str += " %s.rotateX" % object
            command_str += " %s.rotateY" % object
            command_str += " %s.rotateZ" % object
        command_str += ";"
        mel.eval(command_str)

        # Get configuration of selection
        n_keyframes = self.n_keyframes_slider.value()
        selection = self.selections[n_keyframes]["selection"]
        start = selection[0]
        end = selection[-1]

        # Turn off ghosting first!
        mel.eval("unGhostAll")

        # Save the current animation
        self.save_animation(objects, start, end)

        # Apply reduction
        reduce_keyframes(selection)

    def get_n_keyframes(self):
        return self.n_keyframes_slider.value()

    def get_error(self, n_keyframes=-1, normalized=True):
        n = n_keyframes if n_keyframes != -1 else self.n_keyframes_slider.value()

        if normalized:
            min_n = min(self.selections.keys())
            return self.selections[n]["error"] / self.selections[min_n]["error"]
        else:
            return self.selections[n]["error"]

    def get_selection_of_n_keyframes(self, n_keyframes):
        return self.selections[n_keyframes]["selection"]

    def get_keyframe_range(self):
        return min(self.selections.keys()), max(self.selections.keys())

    def update_visualization(self):
        
        # Get data for error graph
        n_keyframes = self.n_keyframes_slider.value()
        self.error_edit.setText("%2.4f" % self.get_error(n_keyframes, normalized=False))
        min_keyframes, max_keyframes = self.get_keyframe_range()
        xs = [float(n - min_keyframes) / float(max_keyframes - min_keyframes) for n in range(min_keyframes, max_keyframes + 1)]
        ys = [self.get_error(n, normalized=True) for n in range(min_keyframes, max_keyframes + 1)]
        points = list(zip(xs, ys))

        # Submit data to make error graph
        self.painter.reset_drawing_fns()
        self.painter.add_drawing_fn(DrawingBuilder.create_points_fn(points, DrawingBuilder.red(), size=3))
        self.painter.add_drawing_fn(DrawingBuilder.create_vertical_line_based_on_attribute_fn(self.get_n_keyframes, self.get_keyframe_range, DrawingBuilder.white()))
        self.painter.add_drawing_fn(DrawingBuilder.create_horizontal_line_based_on_attribute_fn(self.get_error, lambda: (0, 1), DrawingBuilder.white()))
        self.painter.activate()
        self.repaint()

        # Update ghosts
        mel.eval("unGhostAll")
        frames = [int(v) for v in self.get_selection_of_n_keyframes(self.n_keyframes_slider.value())]
        objects = cmds.ls(selection=True)
        for object in objects:
            obj_for_ghosting = object
            obj_is_transform = cmds.objectType(object) == 'transform'
            if obj_is_transform: # Change the object to the shape if this is a transform
                obj_for_ghosting = cmds.listRelatives(object, shapes=True)[0]
            cmds.setAttr("%s.ghosting" % obj_for_ghosting, 1)
            cmds.setAttr("%s.ghostingControl" % obj_for_ghosting, 1)
            cmds.setAttr("%s.ghostFrames" % obj_for_ghosting, frames, type="Int32Array")

    def set_n_keyframes_via_text(self):
        value = int(self.n_keyframes_edit.text())
        self.n_keyframes_slider.setValue(value)
        if len(self.selections) > 0:
            self.error_edit.setText("%2.4f" % self.get_error(self.n_keyframes_slider.value(), normalized=False))
            self.update_visualization()
            self.repaint()

    def set_n_keyframes_via_slider(self, value):
        self.n_keyframes_edit.setText(str(value))
        if len(self.selections) > 0:
            self.error_edit.setText("%2.4f" % self.get_error(self.n_keyframes_slider.value(), normalized=False))
            self.update_visualization()
            self.repaint()
