# Flowizi

Flowizi is a CLI app that simplifies your workflow when you join a meeting

### Key features

- Add and join meetings without having to open a browser manually
- Automatically open any websites or apps that are part of your workflow when you join a meeting
- Start recording the screen after joining a meeting and storing the video locally

### Installation

To download Flowizi, go to the [Releases](https://github.com/jeangiraldoo/flowizi/releases) section of this repository and download the .exe for the latest release (or the release you prefer) in the assets section. At the moment there's no release for MacOS or Linux, but stay tuned!

The .exe file behaves like a script. You need to move it to the directory where you want it to reside. Once it's there, you can run it using the terminal.

### How to use it

Flowizi revolves around environments and elements. An environment is like a container, it is a representation of your workflow. Let's say that you are working on a project, every time you work on that project you need to open a specific file, a website and maybe a text editor; the concept of the project would be the environment, the file, website and text editor would be elements of that environment.

Type `flowizi.exe list`. This command will show you what environments you have created. Since it is the first time you use Flowizi, you will not have an environment.

Let's create an environment. Type `flowizi.exe add name`, replace "name" with the name you want for the environment.

You can add elements to that environment by using a flag, -w is used for websites and -m for meetings. `flowizi.exe add -w name link env_name` will create a meeting with whatever name you set for "name", and will add it to the environment that has the same name you typed in the "env_name" argument. Adding meetings works exactly the same, just with the -m flag.

If you want to remove an entire environment, you can use the remove command. Type `flowizi.exe remove environment`. "Environment" is the name of the environment you wish to remove.

Removing elements from an environment (without removing the environment itself) is just as easy, you just have to use the remove command with either the -w or -m flag, following the same structure you used when you added those elements in the first place, but with the remove command instead of the add command. Type `flowizi.exe remove -w name environment` to remove a website. `flowizi.exe remove -m name environment` removes a meeting.

The system command will show the current user you are logged in as and the name of your operating system.

Finally, you can open everything contained in a container with the start command: `flowizi.exe start environment` 
