# Change Log

## [0.1.0] - 2022-16-08
First major release. Provides user with the bare essentials to load projects and scan image data.

### Added
- Ability to load projects
- Ability to view raw scan images
- Ability to view gridded scan data with custom HKL bounds and pixel counts
- ImageTool controller for selecting image to view

## [0.1.1] - 2022-23-08
Basic color mapping. 

### Added
- ColorMapWidget for creating custom color maps

## [0.1.2] - 2022-08-09
Additional color mapping functions and mouse tracking

### Added
- Option to change maximum pixel value of a color map
- Mouse info section that tracks HKL positions and intensity of a pixel when hovered over

### Fixed
- Color bars now accurately represent an image's color map

## [0.1.3] - 2022-20-09
Line segment ROI's and QOL fixes

### Added
- Line segment ROI objects that can be added to the main ImagePlot that will produce a 2D slice of the contained pixels
- Basic keyboard shortcuts (Close: Ctrl+W or Ctrl+Q, Minimize: Ctrl+-, Full Screen: Ctrl+Shift+F)

### Fixed
- Faster color mapping
- Gridded Data: Image is automatically scaled when dimension order changes
- Error handling for mouse tracking
- Maximum direction pixel count for gridding decreased from 1000px to 750px