import maya.cmds as cmds

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

