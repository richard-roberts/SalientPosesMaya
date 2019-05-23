import math

from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
from shiboken2 import wrapInstance

from maya import OpenMayaUI as omui 
import maya.cmds as cmds
import maya.mel as mel

import salient_utils
import salient_api

def _reload():
    reload(salient_utils)
    reload(salient_api)

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

def getMayaMainWindow():
    mayaPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaPtr), QtWidgets.QWidget)
    
_win = None
def show():
    global _win
    if _win == None:
        _win = SalientPosesDialog(parent=getMayaMainWindow())
    _win.show(dockable=True)

class SalientPosesDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(SalientPosesDialog, self).__init__(parent)
        self.my_parent = parent
        
        self.selections = {}
        self.saved_animations = []

        def init_ui(): 
            start = int(cmds.playbackOptions(query=True, minTime=True))
            end = int(cmds.playbackOptions(query=True, maxTime=True))

            vbox = salient_utils.UIBuilder.vertical_box(parent=self)

            # OpenCL device choice
            listed_devices = [v for v in cmds.salientOpenCLInfo().split("\n") if v != ""]
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            salient_utils.UIBuilder.label(hbox, "OpenCL Device")
            self.opencl_device_combo = salient_utils.UIBuilder.make_combo(hbox, listed_devices)
            
            # Start frame box
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            salient_utils.UIBuilder.label(hbox, "Start End")
            self.start_edit = salient_utils.UIBuilder.line_edit(hbox, str(start))

            # End frame box
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            salient_utils.UIBuilder.label(hbox, "End Frame")
            self.end_edit = salient_utils.UIBuilder.line_edit(hbox, str(end))

            # Fixed keyframes text field
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            salient_utils.UIBuilder.label(hbox, "Fixed Keyframes")
            self.fixed_keyframes_edit = salient_utils.UIBuilder.line_edit(hbox, "")

            # N keyframes text field
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            salient_utils.UIBuilder.label(hbox, "N Keyframes")
            self.n_keyframes_edit = salient_utils.UIBuilder.line_edit(hbox, str(3), self.set_n_keyframes_via_text)

            # Error text field
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            salient_utils.UIBuilder.label(hbox, "Error")
            self.error_edit = salient_utils.UIBuilder.line_edit(hbox, "%2.4f" % -1)
            self.error_edit.setEnabled(False)

            # N keyframes slider
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            self.n_keyframes_slider = salient_utils.UIBuilder.slider(hbox, 3, end - start + 1, 1, 3, self.set_n_keyframes_via_slider)

            # Error drawing
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            self.painter = salient_utils.DrawingBuilder.make(hbox, self, (200, 200))

            # Actions
            hbox = salient_utils.UIBuilder.horizontal_box(add_to=vbox)
            salient_utils.UIBuilder.label(hbox, "Actions")
            salient_utils.UIBuilder.button(hbox, "Evaluate", fn=self.do_select)
            salient_utils.UIBuilder.button(hbox, "Reduce", fn=self.do_reduce)
            self.undo_button = salient_utils.UIBuilder.button(hbox, "Undo (0)", fn=self.revert_to_saved)

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

        start = int(self.start_edit.text())
        end = int(self.end_edit.text())
        self.selections = salient_api.select_keyframes(cl_platform_ix, cl_device_ix, start, end, fixed_keyframes)

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
        salient_api.reduce_keyframes(selection)

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
        self.painter.add_drawing_fn(salient_utils.DrawingBuilder.create_points_fn(points, salient_utils.DrawingBuilder.red(), size=3))
        self.painter.add_drawing_fn(salient_utils.DrawingBuilder.create_vertical_line_based_on_attribute_fn(self.get_n_keyframes, self.get_keyframe_range, salient_utils.DrawingBuilder.white()))
        self.painter.add_drawing_fn(salient_utils.DrawingBuilder.create_horizontal_line_based_on_attribute_fn(self.get_error, lambda: (0, 1), salient_utils.DrawingBuilder.white()))
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
