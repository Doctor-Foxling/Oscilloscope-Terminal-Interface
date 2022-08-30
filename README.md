# Oscilloscope-Terminal-Interface

## File Structure

<img src="https://github.com/Doctor-Foxling/Oscilloscope-Terminal-Interface/blob/master/images/file%20structure.png">

## Overview

The server is a console-based application:

<img src="https://github.com/Doctor-Foxling/Oscilloscope-Terminal-Interface/blob/master/images/term%201.png">

It is a multithreaded application with three threads running:

<ul>
<li> Wave-Generation Thread: Generates the square wave for channel one and provides end-points to access different parts of the wave (e.g. start, stop points, xref etc.). It also creates an (simulated) internal memory represented by json files (storing 1320 points), storing wave information beyond the range of the array storing 120 points.</li>
<li> Data Streaming Thread:- Streams the square wave voltage data via a UDP socket to the client. </li>
<li> Main Thread: The main server logic. Accepts commands from the client via a TCP socket and uses regex to recognize command pattern to separate the types of commands and then detect individual commands via conditional statements. Uses state machines to manage states of different properties (e.g. Channel, Mode etc.) and handles any condition of mutually exclusive states. </li>
</ul>


The Client is a GUI-based, multithreaded application (though the main thread does not have a GUI):

<img src="https://github.com/Doctor-Foxling/Oscilloscope-Terminal-Interface/blob/master/images/term%202.png">

The client has two GUI windows, the first window shown above is where the commands are entered, to interact with the SCPI server. 
The first time the application is opened, and the user enters a command, the user is prompted with a popup window requesting for a username and the protocol.

<img src="https://github.com/Doctor-Foxling/Oscilloscope-Terminal-Interface/blob/master/images/uesrname.png">

Based on the chosen protocol (S (short) or L (long)) the user then is supposed to stick to the chosen protocol when entering the commands.
The second Window is the live-data-streaming window which shows the wave-generated via the Wave-Generation thread on the server side, in real time, transmitted via udp-socket, broadcasting the voltage data of the square-wave.

<img src="https://github.com/Doctor-Foxling/Oscilloscope-Terminal-Interface/blob/master/images/live%20stream.png">

The window also shows the selected channel and the Mode, with the wave-data always saying chan1, because other channels aren’t connected (technically not been coded to generate wave). The channel and Mode info might not be accurate if the client was closed while the server was running and the server is not in the default state when the client is re-opened (however, as soon as the chan or mode is changed again, it will update on the second window).

The user is also provided with a menu system which lets the user do almost everything that he/she could do with the command line.

<img src="https://github.com/Doctor-Foxling/Oscilloscope-Terminal-Interface/blob/master/images/menu%201.png">

You can read the full documentation [Here](https://github.com/Doctor-Foxling/Oscilloscope-Terminal-Interface/blob/master/Documentation/SCPI_sim_docs.docx)




