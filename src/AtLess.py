import argparse
import os
import json
import rpack
import png
import numpy as np

class SpriteSheet:

    def __init__(self, baseFilePath):

        self._baseFilePath = baseFilePath

        r = png.Reader(f'{baseFilePath}.png')

        data = r.read()

        self._dimensions = (data[0], data[1])
        self._rows = np.vstack(list(map(np.uint16, data[2])))

        with open(f'{baseFilePath}.json') as f:
            self._JSON = json.load(f)

            if (not type(self._JSON['frames']) == list):
                self._JSON['frames'] = [frame for _,frame in self._JSON['frames'].items()]
                self._JSON['frames'][0]['filename'] = f'{baseFilePath}_idle_down_0'

        self._position = None

    @property
    def dimensions(self) -> tuple[int, int]:
        return self._dimensions
    
    @property
    def rows(self):
        return self._rows
    
    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def JSON(self) -> dict:
        return self._JSON

class Atlas:

    def __init__(self, inputDir, exportDir=None): 

        self._inputDirectory = inputDir
        self._PNGData = None
        self._JSONData = None
        self._spriteSheets = []

        if exportDir:

            self.exportInputs(exportDir)
            self.initSpriteSheets(exportDir)
        
        else: 
            self.initSpriteSheets(inputDir)

        self._dimensions = rpack.bbox_size([ss.dimensions for ss in self._spriteSheets], [ss.position for ss in self._spriteSheets])

    @property
    def dimensions(self) -> tuple[int, int]:
        return self._dimensions

    def pasteAtLoc(self, src: np.array, dest: np.array, x, y):

        dest[y:src.shape[0] + y, x:src.shape[1] + x] = src

        return dest

    def exportInputs(self, exportDir):

        print(exportDir)
        for filename in os.listdir(self._inputDirectory):

            (baseFilename, extension) = os.path.splitext(filename)

            if extension == ".aseprite":

                jsonPath = os.path.join(exportDir, f'{baseFilename}.json')
                pngPath = os.path.join(exportDir, f'{baseFilename}.png')
                file = os.path.join(self._inputDirectory, filename)

                command = f'aseprite --batch --data "{jsonPath}" --format json-array --sheet "{pngPath}" --sheet-type packed --split-layers --split-tags --all-layers --filename-format "{{title}}_{{tag}}_{{layer}}_{{frame}}" --trim {file}'

                print(command)
                os.system(command)

    def initSpriteSheets(self, spriteSheetDir):

        for filename in os.listdir(spriteSheetDir):

            (baseFilename, extension) = os.path.splitext(filename)
            
            if extension == ".png":
                
                self._spriteSheets.append(SpriteSheet(f'{spriteSheetDir}/{baseFilename}'))

        rectangles = [spriteSheet.dimensions for spriteSheet in self._spriteSheets]
        positions = rpack.pack(rectangles)

        for position, spriteSheet in zip(positions, self._spriteSheets):
            spriteSheet.position = position

    def createPNGData(self):

        newPNG = np.zeros((self._dimensions[1], self._dimensions[0], 4), dtype = 'int')

        for spriteSheet in self._spriteSheets:

            srcPNG = spriteSheet.rows
            srcPNG = np.reshape(srcPNG, (spriteSheet.dimensions[1], spriteSheet.dimensions[0], 4))
            newPNG = self.pasteAtLoc(srcPNG, newPNG, spriteSheet.position[0], spriteSheet.position[1])

        newPNG = np.reshape(newPNG, (-1, self._dimensions[0] * 4))

        newPNG = list(map(np.uint16, newPNG))
        newPNG = list(map(list, newPNG))

        self._PNGData = newPNG

    def createJSONData(self):

        self._JSONData = {
            'meta': {
                'size': {
                    'w': self._dimensions[0],
                    'h': self._dimensions[1]
                }
            },
            'spritesheets': []
        }

        for spriteSheet in self._spriteSheets:
            
            spriteSheetData = {}

            spriteSheetData['name'] = spriteSheet.JSON['meta']['image'].split('.')[0]
            spriteSheetData['size'] = spriteSheet.JSON['meta']['size']
            spriteSheetData['spriteSize'] = spriteSheet.JSON['frames'][0]['sourceSize']
            spriteSheetData['position'] = {
                'x': spriteSheet.position[0],
                'y': spriteSheet.position[1]
            }
            spriteSheetData['animations'] = []

            animationData = {}

            for frame in spriteSheet.JSON['frames']:
                
                nameSplit = frame['filename'].lower().split('_')
                tempAnimationName = '_'.join(nameSplit[1:3])

                currAnimation = animationData.get(tempAnimationName, {
                    'name': nameSplit[1],
                    'direction': nameSplit[2],
                    'numFrames': 0,
                    'frames': []
                })

                currFrame = {
                    'frameNumber': nameSplit[3],
                    'duration': frame['duration'],
                    'size': {
                        'w': frame['frame']['w'],
                        'h': frame['frame']['h']
                    },
                    'position': {
                        'x': frame['frame']['x'] + spriteSheet.position[0],
                        'y': frame['frame']['y'] + spriteSheet.position[1]
                    },
                    'offset': {
                        'x': frame['spriteSourceSize']['x'],
                        'y': frame['spriteSourceSize']['y']
                    }
                }

                currAnimation['frames'].append(currFrame)
                currAnimation['numFrames'] = currAnimation['numFrames'] + 1

                animationData[tempAnimationName] = currAnimation

            spriteSheetData['animations'] = [animation for _, animation in animationData.items()]

            self._JSONData['spritesheets'].append(spriteSheetData)

    def toPNG(self, outFile):

        if self._PNGData == None:
            self.createPNGData()
            
        with open(outFile, 'wb') as f:
            w = png.Writer(self._dimensions[0], self._dimensions[1], greyscale=False, alpha=True)
            w.write(f, self._PNGData)

    def toJSON(self, outFile):

        if self._JSONData == None:
            self.createJSONData()

        with open(outFile, 'w') as f:
            json.dump(self._JSONData, f, indent=4)
    
    def toPlaceholders(self, outDir):

        os.makedirs(outDir, exist_ok = True)

        for spriteSheet in self._spriteSheets:

            referenceFrame = spriteSheet.JSON['frames'][0]

            newPNG = np.zeros((referenceFrame['sourceSize']['h'], referenceFrame['sourceSize']['w'], 4), dtype = 'int')

            offset = (
                referenceFrame['spriteSourceSize']['x'],
                referenceFrame['spriteSourceSize']['y']
            )

            dimensions = (
                referenceFrame['spriteSourceSize']['w'],
                referenceFrame['spriteSourceSize']['h']
            )

            position = (
                referenceFrame['frame']['x'],
                referenceFrame['frame']['y']
            )

            srcPNG = spriteSheet.rows
            srcPNG = np.reshape(srcPNG, (spriteSheet.dimensions[1], spriteSheet.dimensions[0], 4))
            srcPNG = srcPNG[position[1]:position[1]+dimensions[1], position[0]:position[0]+dimensions[0]]
            newPNG = self.pasteAtLoc(srcPNG, newPNG, offset[0], offset[1])

            newPNG = np.reshape(newPNG, (-1, referenceFrame['sourceSize']['w'] * 4))

            newPNG = list(map(np.uint16, newPNG))
            newPNG = list(map(list, newPNG))

            with open(f"{outDir}/{spriteSheet.JSON['meta']['image']}", 'wb') as f:
                w = png.Writer(referenceFrame['sourceSize']['w'], referenceFrame['sourceSize']['h'], greyscale=False, alpha=True)
                w.write(f, newPNG)

def createParser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog='Sprite Atlas Tool', 
        description=('Sprite Atlas Creator'),
        epilog='\n')

    parser.add_argument('input', metavar='I', nargs='?', type=str, help='Input folder')
    parser.add_argument('output', metavar='O', nargs='?', type=str, help='Output folder', default='spriteAtlas')

    return parser

if __name__ == "__main__":

    args = createParser().parse_args()



    if (args.output[-1] == '\\' or args.output == '/'):
        args.output = args.output[:-1]

    (outputHead, outputBase) = os.path.split(args.output)

    exportDir = os.path.join(outputHead, outputBase, 'exports')

    os.makedirs(args.output, exist_ok = True)
    os.makedirs(exportDir, exist_ok = True)

    atlas = Atlas(args.input, exportDir=exportDir)

    atlas.toPNG(os.path.join(outputHead, outputBase, f'{outputBase}.png'))
    atlas.toJSON(os.path.join(outputHead, outputBase, f'{outputBase}.json'))
    atlas.toPlaceholders(os.path.join(outputHead, outputBase, 'placeholders'))