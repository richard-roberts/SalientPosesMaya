# Salient Poses (Maya implementation)

Salient Poses is an algorithm that
uses a technique called "keyframe reduction"
to convert hard-to-edit motion capture
into easy-to-edit keyframe animation.
This project contains a **Maya plug-in** that enables
artists to run Salient Poses directly inside of Maya.


# Stuck?

See [salientposes.com](https://salientposes.com/)
for further information, selected results, and links to academic work.

Please report any issues, I'm always happy to help! Click here to join the [Salient Poses Slack Channel](https://join.slack.com/t/salientposes/shared_invite/enQtNDU1MTM0Nzk4Mjk0LWY5MzlhYTNkMjAzM2ZkYWNmNjY5YWViNWMzZDVkNzkxYTFlYmFjMjAxZWUzOGM4MzQ0OGU0YThmM2I5N2Y1MTI) or otherwise feel free to post something to the [issues board](https://github.com/richard-roberts/SalientPosesPerformance/issues).

**Note**: I've added an error to report the plugin missing when not installed and loaded. Documentation for installing plugins can be [found here](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-Customizing/files/GUID-FA51BD26-86F3-4F41-9486-2C3CF52B9E17-htm.html). Please ensure you have the plugin installed correctly before reporting issues.


# Getting Started

0. Ensure you have an OpenCL compatible device. Most Intel, AMD, and NVIDIA devices are compatible.
1. Grab the [latest release](https://github.com/richard-roberts/SalientPosesMaya/releases/tag/0.2)
2. Install the plugin; here is the [documentation for installing plugins](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-Customizing/files/GUID-FA51BD26-86F3-4F41-9486-2C3CF52B9E17-htm.html).
3. Load the shelf-script
4. Follow along with the [video tutorial](https://www.youtube.com/watch?v=WzFoJoXZO-g)


# What's in the box?

This repository presents an implementation of the Salient Poses algorithm as a command-based **Maya plug-in** that I've designed for interactive use in Maya by motion-editors, animators, technical artists, and hobbyists. The tool is built with `C++` and uses `OpenCL` to redistribute some of the heavier number crunching. 

Since this implementation is designed for interactive use, it comes with its own GUI. Using the interface you can specify parameters around the selection and then apply that selection to perform the keyframe-reduction. Once applied, the resulting animation consists of only the keyframes paired with curves that provide the inbetweens - much like hand-crafted animation.

*Note: there is also a standalone [Salient Poses](https://github.com/richard-roberts/SalientPosesPerformance) implementation.*

## Usage

*Note: don't forget to check out the [video tutorial](https://www.youtube.com/watch?v=WzFoJoXZO-g) as well.*

The interface guides you through the two phases: **selection** and **reduction**. Selection is process of choosing a range of potential keyframes for a given animation. Reduction is the process of first removing keyframes and then tweaking the resulting inbetweens to recreate the original motion. The interface will help you to manage these two steps.


1. Open the tool by pressing the menu button on the shelf, here's what you should see:

![A look at the interface](http://richardroberts.co.nz/images/hosting/spm-a-look-at-the-interface.png) 

2. **Start / End Frame**. 
First check that the start and end frames of your timeline are set appropriately.
Salient Poses will use the timeline to infer which part of your animation 
it should be applied to.

2. **Fixed Keyframes**. 
Next, enter any particular keyframes that you would
like to ensure are kept during reduction.
Enter any keyframes you want kept as as comma-separated whole numbers;
for example if you want to keep frames 30, 100, and 150 as keyframes
then you'd specify:
`30,100,150`.
Setting *fixed keyframes* can be important for some editing tasks;
for example, you might want to keep the frame at the very top of a jumping motion
as a keyframe.

3. **Evaluate**.
Now, select a set of animated objects in Maya;
the [outliner](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-Basics/files/GUID-4B9A9A3A-83C5-445A-95D5-64104BC47406-htm.html)
is useful for doing this.
The choice of what to include is up to you -
explore different choices to get a feeling for how the tool works.
If you're just interested in compression,
selecting the joints along a character's spine and limbs is generally the best option.
Otherwise, if you've got a specific change to make,
I find that choosing objects around the leading part is most useful
(the leading part is an animation term that
I first read about in John Lasseter's
[famous paper](https://courses.cs.washington.edu/courses/cse458/11au/resources/lasseter.pdf)).
*Remember,
the objects you select **don't** have to be those used later in the reduction step*.
Once you've got the objects selected,
**press the evaluate button**
and the tool will starting computing a range of *optimal* selections.

*Note: The word optimal means that each particular set of keyframes is
as-good-as-possible in terms of how well the simplified animation
will recreate the original motion.*

![Choosing a selection](http://richardroberts.co.nz/images/hosting/spm-choosing-a-selection.png) 

4. **Reduction**. 
At this point,
you need only **choose a particular set of keyframes**
and then apply the reduction.
You do this by adjusting the slider in the interface.
You'll see the keyframes illustrated interactively as blue silhouettes.
Once you've found a set of keyframes you would like to try,
**select the objects for reduction**
(this will usually be all controls for the character and any other props)
and press the `Reduce` button.
This will take a few seconds. 

![Before and After](http://richardroberts.co.nz/images/hosting/spm-before-and-after.png)

After you've applied the reduction,
play back the animation and also
examine the graph editor to see if the
result is satisfactory.
There's no right answer;
but generally you're looking for smooth curves
that look similar to the original.

5. **Explore**.
Perhaps the result you get the first time
wasn't quite right. Or maybe it was and that's great!
In either case,
the tool is designed to help you explore
and compare multiple solutions quickly.
You can explore by:

- using the slider to increase and decrease the number of keyframes,
- changing the start and end frame, and also
- setting fixed keyframes.

You can even apply a reduction,
do a
[playblast](https://knowledge.autodesk.com/support/maya-lt/learn-explore/caas/CloudHelp/cloudhelp/2017/ENU/MayaLT/files/GUID-1C6EDC8D-DA67-490E-81F1-1205336DEBD9-htm.html), 
and then undo the reduction. 
*Note: the undo button works like a stack,
you can do multiple reductions and then undo each one.*
As you explore,
its important to think carefully about
the **trade-off between compression and error**.
If you are using the tool to compress assets for a video-game,
you want to ensure that you retain a high level of detail
while using as few keyframes as possible. 
This will help you to save on the memory footprint for your game.
If you are using the tool for editing, 
try to examine how well the keyframes are distributed:
is there enough keyframes for you to make an adjustment
without distorting the motion?
The **graph** within the interface helps to communicate this tradeoff
(the red line indicates detail is lost for the current reduction).

**That's it.**
Please remember that I'm happy to help you along the way if you ever get stuck.
Feel free to jump onto the
[Slack Channel](https://join.slack.com/t/salientposes/shared_invite/enQtNDU1MTM0Nzk4Mjk0LWY5MzlhYTNkMjAzM2ZkYWNmNjY5YWViNWMzZDVkNzkxYTFlYmFjMjAxZWUzOGM4MzQ0OGU0YThmM2I5N2Y1MTI)
and chat with me, or otherwise check the
[Salient Poses website](https://salientposes.com/) for more information!

# Code Structure

This algorithm works in a few steps, which I like to think of as:

1. **analysis**, building a table that expresses the importance of all potential keyframes,
2. **selection**, optimally choosing a set of poses for each level of compression, and
3. **reconstruction**, where we create the new animation from a given set of poses.

If you'd like to peek into the code,
it's best to start with the
[SalientPoses - Performance](https://github.com/richard-roberts/SalientPosesPerformance)
project (a high-performance command-line tool for running the algorithm offline).

If you're just interested in changing the interface, start by looking at [this Python file](https://github.com/richard-roberts/SalientPosesMaya/blob/master/scripts/salient_gui.py) and then some of the other files in the 
[scripts](https://github.com/richard-roberts/SalientPosesMaya/blob/master/scripts) directory. The implementation of the menu uses [PySide2](https://wiki.qt.io/PySide2) and should be familiar enough to anyone with a little experience using Python.

Otherwise, start by looking at the [Error Table](https://github.com/richard-roberts/SalientPosesPerformance/blob/5354a4f383fb6b8451cecae477872a475c9c833a//src/ErrorTable.hpp) class (this performs the analysis step), then the [Selector](https://github.com/richard-roberts/SalientPosesPerformance/blob/5354a4f383fb6b8451cecae477872a475c9c833a//src/Selector.hpp) class (this chooses optimal set of poses), and also the [Interpolator](https://github.com/richard-roberts/SalientPosesPerformance/blob/5354a4f383fb6b8451cecae477872a475c9c833a//src/Interpolator.hpp) class (this performs reconstruction using a basic curve-fitting technique). 

Once you get that far, check out the [SelectCommand](https://github.com/richard-roberts/SalientPosesMaya/blob/master/src/SelectCommand.hpp) and the [ReduceCommand](https://github.com/richard-roberts/SalientPosesMaya/blob/master/src/ReduceCommand.hpp) files. These two classes use the `Error Table`, `Selector`, and `Interpolator` to realize the algorithm in Maya.

If you've got this far and wait more information, jump on the [Slack Channel](https://join.slack.com/t/salientposes/shared_invite/enQtNDU1MTM0Nzk4Mjk0LWY5MzlhYTNkMjAzM2ZkYWNmNjY5YWViNWMzZDVkNzkxYTFlYmFjMjAxZWUzOGM4MzQ0OGU0YThmM2I5N2Y1MTI) with me or otherwise check the [Salient Poses website](https://salientposes.com/) for more information!
