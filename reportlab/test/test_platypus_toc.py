"""Tests for the Platypus TableOfContents class.

Currently there is only one such test. Most such tests, like this
one, will be generating a PDF document that needs to be eye-balled
in order to find out if it is 'correct'.
"""


import sys, os, tempfile
from os.path import join, basename, splitext
from math import sqrt

from reportlab.test import unittest
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus import tableofcontents0
from reportlab.platypus.tableofcontents0 import TableOfContents0
from reportlab.platypus.tables import TableStyle, Table


def mainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."
    
    canvas.saveState()

    canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()
    

class MyTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."
    
    _invalidInitArgs = ('pageTemplates',)
    
    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1], mainPageFrame)
        self.addPageTemplates(template)


    def afterFlowable(self, flowable):
        "Takes care of registering TOC entries."
        
        if flowable.__class__.__name__ == 'Paragraph':
            styleName = flowable.style.name
            if styleName[:7] == 'Heading':
                level = int(styleName[7:])
                text = flowable.getPlainText()
                pageNum = self.page 
                self.notify0('TOCEntry', (level, text, pageNum))


def makeHeadingStyle(level, fontName='Times-Roman'):
    "Make a heading style for different levels."

    assert level >= 0, "Level must be >= 0."
    
    PS = ParagraphStyle
    size = 24.0 / sqrt(1+level)
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0)

    return style


def makeTocHeadingStyle(level, delta, epsilon, fontName='Times-Roman'):
    "Make a heading style for different levels."

    assert level >= 0, "Level must be >= 0."
    
    PS = ParagraphStyle
    size = 12
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0,
               firstLineIndent = -epsilon,
               leftIndent = level*delta + epsilon)

    return style


class TocTestCase(unittest.TestCase):
    "Test TableOfContents0 class (eyeball-test)."
    
    def test1(self):
        """Test story with TOC and a cascaded header hierarchy.

        The story contains exactly one table of contents that is
        immediatly followed by a list of of cascaded levels of
        header lines, each nested one level deeper than the
        previous one."""

        maxLevels = 12

        # Create styles to be used for document headers
        # on differnet levels.
        headlineLevelStyles = []
        for i in range(maxLevels):
            headlineLevelStyles.append(makeHeadingStyle(i))

        # Create styles to be used for TOC entry lines
        # for headers on differnet levels.
        tocLevelStyles = []
        d, e = tableofcontents0.delta, tableofcontents0.epsilon
        for i in range(maxLevels):
            tocLevelStyles.append(makeTocHeadingStyle(i, d, e))

        # Build story containinf one TOC followed by some
        # cascaded levels of header lines, each nested one
        # level deeper than the previous one.
        story = []
        toc = TableOfContents0()
        toc.levelStyles = tocLevelStyles
        story.append(toc)

        for i in range(maxLevels):
            story.append(Paragraph('HEADER, LEVEL %d' % i,
                                   headlineLevelStyles[i]))

        tempfile.tempdir = os.curdir
        path = join(tempfile.tempdir, 'test_platypus_toc.pdf')
        doc = MyTemplate(path)
        doc.multiBuild0(story)
        

def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(TocTestCase('test1'))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
