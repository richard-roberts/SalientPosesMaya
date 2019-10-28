# Salient Poses (Maya implementation)

Salient Poses is an algorithm that
uses a technique called "keyframe reduction"
to convert hard-to-edit motion capture
into easy-to-edit keyframe animation.
This project contains a **Maya module** that enables
artists to run Salient Poses directly inside of Maya.

![thumb](doc/images/salientPosesThumb.png)

## Want to jump right in?

Grab the [latest release](https://github.com/richard-roberts/SalientPosesMaya/releases/tag/0.3), [add it to Maya](#getting-started), and then follow along with the [video tutorial](https://youtu.be/OpKDwciLEac)!

## Table Of Contents

1. [Easy-to-Edit Motion Capture!](#easy-to-edit-motion-capture)
2. [Getting Started](#getting-started)
3. [What's in this Project?](#whats-in-this-project)

Please post bugs, feature requests, and other issues to the
[issues board](https://github.com/richard-roberts/SalientPosesMaya/issues).

Easy-to-Edit Motion Capture!
----------------------------

Motion capture has become a **core component** of the animation pipeline in the visual effects industry. Whether it's a live-action blockbuster film or an indie game being developed in a back-alley office, motion capture is likely to be involved. While this technology is awesome - it allows actors to truly embody a fantasy character - it does have its problems.

#### The Problem

Say we start off with a mocap animation (here's one that I grabbed from [Adobe's Mixamo](https://www.mixamo.com)):

![Salient Example (Original)](doc/images/Salient_Example_1.gif)

While the animation looks nice, it actually has lots of [keyframes](https://en.wikipedia.org/wiki/Key_frame). Let's take a look at the keyframes, visualized here as blue outlines. There are so many keyframes; one for every frame. In this case there are 60 per second!

![Salient Example (Mocap Keyframes)](doc/images/Salient_Example_2.png)

While having all of these keyframes involved is necessary during recording - we want accurately capture the actor's performance precisely - they involve a large memory footprint (problematic for video games) and make the motion hard to change (problematic for motion editors). Here's a picture of just **some** of the data for the animation above; can  you imagine loading all the animations for a protagonist character in a video game (there are sometimes thousands of unique motion clips) or trying to adjusting the motion using this data:

![Salient Example (Mocap Data)](doc/images/Salient_Example_3.png)

#### The Solution

To address this problem, I developed an algorithm that uses **optimal keyframe reduction** to simplify motion capture (or other types of animation that have excessive keyframes). Titled "Salient Poses", this algorithm can be used to convert motion capture into hand-crafted keyframe animation. It can also be used to compress and visual the animation too!

More precisely, the algorithm works by finding sets of important keyframes. In each set, the choice of keyframes is organized so that it can reconstruct the original motion as accurately as possible. Here's an illustration of one possible optimal set of keyframes selected for the animation above:

![Salient Example (Selected Keyframes)](doc/images/Salient_Example_4.png)

Comparing these keyframes to the original motion-capture, we can already see the benefit: the motion can be expressed with fewer poses. Having fewer poses in the animation means a **smaller memory footprint** and also that **editors can edit in less time** (fewer keyframes mean fewer adjustments). And, furthermore, the data is now much sparser than before:

![Salient Example (Data Before And After)](doc/images/Salient_Example_5.png)

With all that done, the last step is to create a new animation using only these keyframes. To do this the algorithm performs a curve fitting step to ensure that the [inbetweens](https://en.wikipedia.org/wiki/Inbetweening) best recreate the original animation.

![Salient Example (Data Before And After)](doc/images/Salient_Example_6.png)

#### Before and After

To sum the whole process up, here's a look at the original animation (right side) and the same animation after compression with Salient Poses (left side). In this case, the compressed animation contains only the seven poses from displayed above, paired with a well-fitted  spline interpolation.

![Salient Example (Anim Before And After)](doc/images/Salient_Example_7.gif)



## Getting Started

Getting the module installed is simple. The steps are:

1. Download the latest version from the [releases page](https://github.com/richard-roberts/SalientPosesMaya/releases)
2. Configure the Maya module path to include Salient Poses
3. Set the `SalientPoses` plug-in to autoload
4. Load the `SalientPoses` shelf
5. Click the shelf button to open the GUI
6. See the [tutorial video](https://youtu.be/OpKDwciLEac).


Each release is a compressed file that contains a compiled plug-in file and a scripts directory.
The easiest way to add the plug-in and scripts to Maya is to load the compiled plug-in file using [Maya's Plug-in Manager](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-Customizing/files/GUID-2CF7D90B-EF10-40D1-9129-9D401CCAB952-htm.html). On Windows you are looking to select `SalientPosesMaya.mll`, on OSX its `SalientPosesMaya.bundle`, and Linux its `SalientPosesMaya.so`. 

## What's in this project?

This repository presents an implementation of the Salient Poses algorithm as a command-based **Maya plug-in** paired with an interface that I've designed for interactive use in Maya by motion-editors, animators, technical artists, and hobbyists. The tool is built with `C++` and uses `OpenMP` to redistribute some of the heavier number crunching. 

Since this implementation is designed for interactive use, it comes with its own interface. Using the interface you can specify parameters around the selection and then apply that selection to perform the keyframe-reduction. Once applied, the resulting animation consists of only the keyframes paired with curves that provide the inbetweens - much like hand-crafted animation.

*Note: there's also a [CLI implementation](https://github.com/richard-roberts/SalientPosesPerformance)*
