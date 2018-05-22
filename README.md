# B2RizomUV
RizomUV unwrapping bridge for Blender

<b>How to install:</b>
- Inside Blender navigate to: File -> User Preferences -> Add-ons -> [Install Add-on from File...]

- Select the downloaded zip containing the 'B2Unfold.py.'

- Set the path to the Unfold3D exe/.app in the preferences of the addon

- Save User Settings

- Enjoy! You'll find the options under the Tool Shelf (T)


<b>How it works:</b>

In Blender:

- Select one or multiple objects.

- Navigate to UnfoldUV under the Tool Shelf (Hotkey: T).

- Choose either manual or auto.

<b><i>Auto Tab:</i></b>

- Set up the respective settings for the automation process

- Press 'Auto Unfold!'

<i>"After pressing the auto unfold button, the model will be sent to Unfold3D, and the respective settings that were set up in Blender will be applied. After Unfold3D is finished, it will automatically close the software and import the object/objects back into Blender. The addon will then transfer the UV's back to the original mesh persevering in data such armatures, vertex colors, weights etc."</i>



<b><i>Manuel Tab:</i></b>

- Select one or multiple objects

- Press 'Send'

<i>"This action will export a clean OBJ file and automatically import the object into Unfold3D. You can now utilize the tools provided by the Unfold3D software to cut, unfold and pack the object's UVs. When finished remember to save the object (Ctrl-S)"</i>

- Press 'Get'

<i>"This will reimport the object into Blender and transfer the UVs back to the original object."</i>



<b>Many thanks and happy UV-ing!</b>
