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
- More efficient color mapping
- Gridded Data: Image is automatically scaled when dimension order changes

## [0.1.4] - 2022-07-10
Line segment ROI improvements.

### Added
- 2D to 1D ROI slicing capabilities for both raw and gridded data.

### Fixed
- Pixels with a value of 0 are now represented as blank pixels.

## [0.1.5] - 2022-20-10
Coordinate intervals and 3D image exporting

### Added
- Coordinate intervals to all image plots
- Ability to export 3D images to VTK image data format
- Generalized function for converting 3D numpy arrays to .vti (VTK) files

