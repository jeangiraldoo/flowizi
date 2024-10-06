# Flowizi

Flowizi is a CLI app designed to streamline your workflow. Simply select the apps, files, and websites that make up your work environment, and with one command, open them all simultaneously. You can create multiple environments with different configurations tailored to specific tasks. Plus, Flowizi includes optional screen recording via FFmpeg, automatically capturing your screen when an environment is launched.

# Table of Contents
1. [Features](#features)
2. [Use case](#use-case)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Set up screen-recording](#screen-recording-feature)
6. [Architecture](/docs/arquitecture.md)

## Features
- Automatically open any websites, files or apps that are part of your workflow
- Record the screen after starting an environment and store the video locally
- Set every element to a specific area of the screen automatically when you start your work environment

## Use case

Imagine that you are a developer. Every day you join a meeting on Google Meets, open Intellij IDEA, Spotify, the website for the documentation you need for your project, etc. You can create an environment called "my-project", add the aforementioned things you open every day to it, then type `flowizi start my-project`, and everything will be opened up. From then on you just have to type that command when you want to boot up your work environment!

## Installation

To download Flowizi, go to the [Releases](https://github.com/jeangiraldoo/flowizi/releases) section of this repository and download the .exe for the latest release (or the release you prefer) in the assets section. At the moment there's no release for MacOS or Linux, but stay tuned!

You have to run the installer and click on "install". That's it, it is that easy! Flowizi will be added to your PARH environment variable, hence you can access it from anywhere on your terminal. 

## Usage

These are the available commands:

## `flowizi list` 

List all of the environments that have been created.

## `flowizi add`

Create an empty environment.

Options: <environment_name>

Example: `flowizi add my-project`

## `flowizi add -w`

Add a website to an environmnet.

Options: <website_name> <website_url> <environment_name>

Example: `flowizi add -w spotify https://open.spotify.com/ my-project`

## `flowizi remove`

Remove an environment from the system.

Options: <environment_name>

Example: `flowizi remove my-project`

## `flowizi remove -w`

Remove a website from an environmnet.

Options: <website_name> <environment_name>

Example: `flowizi remove -w spotify https://open.spotify.com/

## `flowizi system`

Print the current user you are logged in as and the name of your operating system.

## `flowizi start`

Start an environment and everything it contains (apps, files, websites, etc).

Options: <environment_name>

Example: `flowizi start my-project`

## `flowizi record`

Toogle screen recording on and off for a specific environment.

Options: `-t`/`-f`

Example: `flowizi record -t my-project`. This will enable automatic screen recording for the my-project environment. `flowizi record -f my-project` will disable the screen recording feature. 

## Screen recording feature

Flowizi uses FFmpeg for the screen recording, you can check the source code for it [here](https://github.com/FFmpeg/FFmpeg). Alongside FFmpeg, Flowizi uses the Stereo Mix audio setting for windows to record the system audio. Flowizi is able to detect your main microphone and use it when recording the screen even if the Stereo Mix setting is not enabled, but it is necessary if you want the system audio to be included in the recorded video. Here is how you can enable this setting:

1. Go to the bottom-right corner of the screen and click on top of the sound icon with the right button. Then click on "Sound settings".

![Screenshot of Windows desktop after right-clicking on the audio icon](/docs/img/stereo_mix1.png)

2. Click on "More sound settings".

![Screenshot of the sound settings available](/docs/img/stereo_mix2.png)

3. Click on the Recording tab.

![Screenshot of the available sound devices and their settings](/docs/img/stereo_mix3.png)

4. Double click Stereo Mix

![Screenshot of the Stereo Mix virtual device](/docs/img/stereo_mix4.png)

5. Click on "Use this device (enable). Then click on "Apply". That's it! Now Flowizi can record system audio.

![Screenshot of the Stereo Mix setting being enabled](/docs/img/stereo_mix5.png)
