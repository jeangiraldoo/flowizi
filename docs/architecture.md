# Arquitecture

#### Class hierarchy in Flowizi

```mermaid
classDiagram
    class Element{
        <<abstract>>
        +String name 
    }
    class ContainedElement{
        <<abstract>>
        +String url
        +start()
    }
    class Application{
        start()
    }
    class File{
        start()
    }
    class Website{
        start()
    }
    class Environment{
        +Application applications[]
        +Website websites[]
        +File files[]
        +Boolean record
        +start()
    }
    class Flowizi{
        +Environment environment_list[]
        +JSON_repository json
        +String version
    }
    class JSON_repository{
        +String name
        +String directory
        +String path
        +Hashmap data[]
        +load()
        +add_environment()
        +add_environment_element()
        +remove_environment()
        +remove_environment_element()
        +exists_environment()
        +exists_environment_element()
        +update_environment_record()
    }
    class ScreenRecorder{
        +String main_microphone
        +ffmpeg_devices[]
        +String ffmpeg_path
        +String stereo
        +formatted_datetime
        +video_output_name
        +audio_output_name
        +merge_output_name
        +start_recording()
    }
    Element <|-- ContainedElement
    Element <|-- Environment
    ContainedElement <|-- Website
    ContainedElement <|-- Application
    ContainedElement <|-- File
    Environment *-- Application
    Environment *-- Website
    Environment *-- File
    ScreenRecorder *.. Environment
    Flowizi *-- JSON_repository
    Flowizi *-- Environment
```
