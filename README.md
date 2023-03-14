# AtLess

## A minimal command-line texture atlas generator for Aseprite

Using tilesheets from individual sprites, along with the generated JSON from Aseprite, create a single tile atlas and an associated JSON file including the metadata of all sprites and individual animations.

Also generated with the atlas is a folder of the primary sprites for use in Tiled (or another map editor), with the base sprite name as the name of the image.

Expects aseprite filename formatted as: ```{title}_{tag}_{layer}_{frame}```

Output JSON:

```json

{
    "meta": {
        "size": {
            "w": xxx,
            "h": xxx
        }
    },
    "spritesheets": [
        {
            "name": "example",
            "size": {
                "w": xxx,
                "h": xxx
            },
            "spriteSize": {
                "w": xxx,
                "h": xxx
            },
            "position": {
                "x": xxx,
                "y": xxx,
            }
            "animations": [
                {
                    "name": "idle",
                    "direction": "down",
                    "numFrames": 1,
                    "frames": [
                        {
                            "frameNumber": 0,
                            "duration": 0,
                            "size": {
                                "w": xxx,
                                "h": xxx
                            },
                            "position": {
                                "x": xxx,
                                "y": xxx,
                            },
                            "offset": {
                                "x": xxx,
                                "y": xxx,
                            }
                        }
                    ]
                },
                {
                    "name": "move",
                    "direction": "down",
                    "numFrames": 2,
                    "frames": [
                        {
                            "frameNumber": 0,
                            "size": {
                                "w": xxx,
                                "h": xxx
                            },
                            "position": {
                                "x": xxx,
                                "y": xxx,
                            },
                            "offset": {
                                "x": xxx,
                                "y": xxx,
                            }
                        },
                        {
                            "frameNumber": 1,
                            "size": {
                                "w": xxx,
                                "h": xxx
                            },
                            "position": {
                                "x": xxx,
                                "y": xxx,
                            },
                            "offset": {
                                "x": xxx,
                                "y": xxx,
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

```

## Usage

```bash
Sprite Atlas Tool [-h] [I] [O]

Sprite Atlas Creator

positional arguments:
  I           Input folder
  O           Base file name. A JSON and PNG file will be created

options:
  -h, --help  show this help message and exit
```
