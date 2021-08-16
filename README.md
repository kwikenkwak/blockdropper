Blockdropper
============

Blender add-on for minecraft animations

Installation
------------

-   Download the blockdropper.py file from this repository
-   Open blender go to Edit-&gt;Preferences-&gt;Add-ons
-   Click on install and choose the blockdropper.py file
-   Click on the box to enable the add-on

Usage
-----

### General usage

First of all you make sure you have the blocks you want to animate as
seperate objects in your blender file, you can do this using jmc2obj or
other programs to load data from your minecraft world

Now you can start animating! The workflow goes like this: you add your
objects to the block array and then when ready you click on "Add
Keyframes" and it will auto-generate the keyframes all by itself

### Explanation for buttons and settings

#### General settings

-   Starting keyframe: keyframe to start animation at this is when the
    first block will begin to fall
-   Dropheight: height in meters the blocks will be dropped from
-   Default delay: the amount of keyframes between each block that has
    it delay setting set to -1 you can use this setting so you can
    change the delay of a lot of blocks at once
-   Default droptime: same as above but for the amount of keyframes it
    will take for the block to reach the destination location
-   Default sense: same as above but for the sense of the movement of
    the blocks
-   Default direction: same as above but for the direction of the
    movement of the blocks

#### Block Array

Here you can see the block array selecting an item here will result in
the item being selected in the viewport

-   You can add and remove an object with the "+" and "-" buttons.
-   The "Find active" button will search the array for the currently
    selected block and select that item if it is found

#### Block settings

Here you can change the settings of the item that is currently selected

-   Object: the object that this item points to
-   Delay: the amount of keyframes until the next block will start to
    fall use -1 to use the default delay
-   Droptime: the amount of keyframes that it will take the block to
    reach te ground, use -1 to use the default droptime
-   Sense: the sense/flow in which the block travels choose between to
    and from original location
-   Direction: the direction of the blocks movement relative to the
    original location of the block

#### Block navigation

Here you find 6 buttons to easily automatically add blocks to the array
and navigate through them. When you click on a button it will try to
find a block that is next to the currently active block in the specific
direction. In order for these buttons to work well blocks should be 1m³
and have there center at x.5 y.5 z.5!

#### Block keyframing

-   Add keyframes: generates the keyframes for the animation
-   Delete keyframes: deletes the applied keyframes of the objects and
    puts them back at there original positions

#### Shortcut key

The add-on also has a shortcut key, if you press Ctrl-W while in the
viewport the addon will automatically add the currently active object to
the array, it will add it after the currently selected block and the
block's settings(except the object property) will be copied from it.
