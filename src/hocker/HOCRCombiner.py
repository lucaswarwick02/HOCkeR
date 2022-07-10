from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from xml.etree.ElementTree import ElementTree
from PIL import Image
import re, sys
import os
from pathlib import Path

class HOCRCombiner():
    def __init__(self, *attributes : str):
        """Takes in a list of the elements which contain text, and a 'title' for the location
        For tesseract, pass in the string 'ocrx_word'
        """
        self.attributes = attributes
        self.hocr_path = None
        self.image_path = None
        self.boxPattern = re.compile('bbox((\s+\d+){4})')

    def _element_coordinates(self, element):
        """
        Returns a tuple containing the coordinates of the bounding box around
        an element
        """
        out = (0,0,0,0)
        if 'title' in element.attrib:
            matches = self.boxPattern.search(element.attrib['title'])
            if matches:
                coords = matches.group(1).split()
                out = (int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]))
        return out

    def locate_image(self, image_path):
        self.image_path = image_path

    def locate_hocr(self, hocr_path):
        self.hocr_path = hocr_path

        self.hocr = ElementTree()
        self.hocr.parse(hocr_path)
    
        # if the hOCR file has a namespace, ElementTree requires its use to find elements
        matches = re.match('({.*})html', self.hocr.getroot().tag)
        if matches:
            self.xmlns = matches.group(1)
        else:
            self.xmlns = ''

    def to_pdf(self, pdf_path, fontname='Courier', fontsize=8):
        if self.hocr_path is None or self.image_path is None or pdf_path is None:
            print("Error: hocr, image, or pdf path not located")
            return

        im = Image.open(self.image_path)
        if 'dpi' in im.info:
            width = float(im.size[0])/im.info['dpi'][0]
            height = float(im.size[1])/im.info['dpi'][1]
        else:
            # we have to make a reasonable guess
            # set to None for now and try again using info from hOCR file
            width = height = None

        ocr_dpi = (300, 300) # a default, in case we can't find it

        # get dimensions of the OCR, which may not match the image
        if self.hocr is not None:
            for div in self.hocr.findall(".//%sdiv"%(self.xmlns)):
                if div.attrib['class'] == 'ocr_page':
                    coords = self._element_coordinates(div)
                    ocrwidth = coords[2]-coords[0]
                    ocrheight = coords[3]-coords[1]
                    if width is None:
                        # no dpi info with the image
                        # assume OCR was done at 300 dpi
                        width = ocrwidth/300
                        height = ocrheight/300
                    ocr_dpi = (ocrwidth/width, ocrheight/height)
                    break # there shouldn't be more than one, and if there is, we don't want it
            
        if width is None:
            # no dpi info with the image, and no help from the hOCR file either
            # this will probably end up looking awful, so issue a warning
            print(f'Warning: DPI unavailable for {self.image_path}. Assuming 96 DPI.')
            width = float(im.size[0])/96
            height = float(im.size[1])/96
      
        # create the PDF file
        pdf = Canvas(pdf_path, pagesize=(width*inch, height*inch), pageCompression=1) # page size in points (1/72 in.)

        # put the image on the page, scaled to fill the page
        pdf.drawInlineImage(im, 0, 0, width=width*inch, height=height*inch)
    
        if self.hocr is not None:
            for line in self.hocr.findall(".//%sspan"%(self.xmlns)):
                if line.attrib['class'] in self.attributes:
                    coords = self._element_coordinates(line)
                    text = pdf.beginText()
                    text.setFont(fontname, fontsize)
                    text.setTextRenderMode(3) # invisible
          
                    # set cursor to bottom left corner of line bbox (adjust for dpi)
                    text.setTextOrigin((float(coords[0])/ocr_dpi[0])*inch, (height*inch)-(float(coords[3])/ocr_dpi[1])*inch)
          
                    # scale the width of the text to fill the width of the line's bbox
                    text.setHorizScale((((float(coords[2])/ocr_dpi[0]*inch)-(float(coords[0])/ocr_dpi[0]*inch))/pdf.stringWidth(str(line.text).rstrip(), fontname, fontsize))*100)
          
                    # write the text to the page
                    text.textLine(str(line.text).rstrip())
                    pdf.drawText(text)
    
        # finish up the page and save it
        pdf.showPage()
        pdf.save()

if __name__ == '__main__':
    root_path = Path(__file__).parent.parent.parent
    
    tests_path = os.path.join(root_path, 'tests')
    image_path = os.path.join(tests_path, 'sample.png')
    hocr_path = os.path.join(tests_path, 'sample.hocr')

    hocr = HOCRCombiner('ocrx_word')
    hocr.locate_image(image_path)
    hocr.locate_hocr(hocr_path)

    hocr.to_pdf(os.path.join(tests_path, 'sample.pdf'))