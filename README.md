# HOCkeR
Python package for combining hOCR files and images into searchable PDFs
# Table of Contents
1. [What is hoCKeR?](#what-is-hocker)
2. [How to install](#how-to-install)
3. [How to Use](#how-to-use)
4. [Credits](#credits)

## What is hOCkeR? <a name="what-is-hocker"></a>
HOCkeR is a Python package for combining hOCR files and images into searchable PDFs. The package lays the text on top of the image, and then creates a PDF with the text and image. The code used is from [HOCRConverter](https://github.com/jbrinley/HocrConverter) by jbrinley. The code was designed for Python 2, therefore does not work with newer version of python, so I created this package as an update to the original code. 

## How to install <a name="how-to-install"></a>
To install the package, run the following command within a python environment:
```bash
pip install hocker
```
If any errors occur whilst installing, try using the .whl file instead [linked here](https://pypi.org/project/hocker/#files)

## How to use hOCkeR <a name="how-to-use"></a>
Below is an example of how to use hOCkeR to combine an png and a .hocr file into a PDF

```python
import hOCkeR as hkr

image_path = 'path/to/image.png'
hocr_path = 'path/to/image.hocr'

# Specify the element in the hocr file to use as the text
hocr = hOCR('ocrx_word') # For tesseract outputs, it is 'ocrx_word'

# Specify the hocr and image path
hocr.locate_image(image_path)
hocr.locate_hocr(hocr_path)

# Output the PDF
hocr.to_pdf('path/to/output.pdf')
```

## Credits & links <a name="credits"></a>
- [hOCKeR](https://pypi.org/project/hocker/) by Lucas Warwick
- [HOCRConverter](https://github.com/jbrinley/HocrConverter) by jbrinley