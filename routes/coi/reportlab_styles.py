import os
import sys

parentPath = os.path.abspath(os.curdir)
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
    getSampleStyleSheet,
    ListStyle,
)
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    Frame,
    flowables,
    BaseDocTemplate,
    PageTemplate,
    PageBreak,
    ListFlowable,
    ListItem,
)
from reportlab.graphics.barcode import code39
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, flowables
from reportlab.pdfbase.pdfmetrics import registerFontFamily, stringWidth

cur_path = os.getcwd() + '/routes/coi'

pdfmetrics.registerFont(
    TTFont("Arial", os.path.join(cur_path, "fonts", "arial.ttf"))
)
pdfmetrics.registerFont(
    TTFont("Arial-Bold", os.path.join(cur_path, "fonts", "arialbd.ttf"))
)
pdfmetrics.registerFont(
    TTFont("Arial-Narrow", os.path.join(cur_path, "fonts", "arialn.ttf"))
)
pdfmetrics.registerFont(
    TTFont("Arial-Narrow-Bold", os.path.join(cur_path, "fonts", "arialnbd.ttf"))
)
pdfmetrics.registerFont(
    TTFont(
        "LiberationSerif",
        os.path.join(cur_path, "fonts", "LiberationSerif-Regular.ttf"),
    )
)
pdfmetrics.registerFont(
    TTFont(
        "LiberationSerif-Bold",
        os.path.join(cur_path, "fonts", "LiberationSerif-Bold.ttf"),
    )
)
pdfmetrics.registerFont(
    TTFont(
        "LiberationSerif-Italic",
        os.path.join(cur_path, "fonts", "LiberationSerif-Italic.ttf"),
    )
)
pdfmetrics.registerFont(
    TTFont(
        "LiberationSerif-BoldItalic",
        os.path.join(cur_path, "fonts", "LiberationSerif-BoldItalic.ttf"),
    )
)

registerFontFamily(
    "Arial",
    normal="Arial",
    bold="Arial-Bold",
    italic="Arial-Bold",
    boldItalic="Arial-Bold",
)
pdfmetrics.registerFontFamily(
    "LiberationSerif",
    normal="LiberationSerif",
    bold="LiberationSerif-Bold",
    italic="LiberationSerif-Italic",
    boldItalic="LiberationSerif-BoldItalic",
)

width, height = letter

# left, right, top, bottom
gutters = (inch / 4, inch / 4, inch / 4, inch / 4)
margins = (inch / 4, inch / 4, inch / 2, inch / 2)
usable_width = width - (gutters[0] + gutters[1])
usable_height = height - (gutters[2] + gutters[3])

# heading, heading line, contact info, and date
styles = dict(
    body=ParagraphStyle(
        "default",
        fontName="Times-Roman",
        fontSize=12,
        leading=15,
        leftIndent=margins[0],
        rightIndent=margins[1],
        firstLineIndent=0,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=5,
        bulletFontName="Times-Roman",
        bulletFontSize=12,
        bulletIndent=0,
        backColor=None,
        wordWrap=None,
        borderWidth=0,
        borderPadding=0,
        borderColor=None,
        borderRadius=None,
        allowWidows=1,
        allowOrphans=0,
        textTransform=None,  # 'uppercase' | 'lowercase' | None
        endDots=None,
        splitLongWords=1,
    )
)
styles["heading"] = ParagraphStyle(
    "bold",
    parent=styles["body"],
    leading=18,
    textTransform="uppercase",
    fontName="Times-Roman",
    bulletFontName="Times-Roman",
    alignment=TA_CENTER,
)

styles["detail"] = ParagraphStyle(
    "detail",
    parent=styles["body"],
    fontSize=10,
    leading=11,
    leftIndent=3,
    rightIndent=3,
)

# used for notes underline
styles["note"] = ParagraphStyle(
    "note",
    parent=styles["body"],
    fontSize=8,
    leading=9.6,
    leftIndent=0,
    rightIndent=0,
    vAlign="TOP",
)

styles["detail-utc"] = ParagraphStyle(
    "detail",
    parent=styles["body"],
    fontSize=10,
    leading=11,
    leftIndent=3,
    rightIndent=3,
    spaceBefore=-20,
    spaceAfter=-15,
)
styles["detail-bold"] = ParagraphStyle(
    "detail", parent=styles["detail"], fontName="Helvetica-Bold"
)
styles["detail-bold-center"] = ParagraphStyle(
    "detail", parent=styles["detail"], fontName="Helvetica-Bold", alignment=TA_CENTER
)
styles["detail-mini"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    fontSize=9,
    leftIndent=0,
    rightIndent=0,
    spaceAfter=0,
    leading=9.6,
)

styles["detail-mini-utc"] = ParagraphStyle(
    "detail-mini-utc",
    parent=styles["detail-utc"],
    fontName="Times-Roman",
    fontSize=6.5,
    leftIndent=-5,
    rightIndent=0,
    spaceAfter=0,
    leading=8,
)
styles["detail-mini-utc-addons"] = ParagraphStyle(
    "detail-mini-utc",
    parent=styles["detail-utc"],
    fontName="Times-Roman",
    fontSize=7.5,
    leftIndent=-5,
    rightIndent=0,
    spaceAfter=0,
    leading=8,
)
styles["detail-mini-utc-right"] = ParagraphStyle(
    "detail-mini-utc",
    parent=styles["detail-utc"],
    fontName="Times-Roman",
    fontSize=6.5,
    leftIndent=-5,
    rightIndent=0,
    spaceAfter=0,
    leading=8,
    alignment=TA_RIGHT,
)

styles["detail-mini-utc-left"] = ParagraphStyle(
    "detail-mini-utc",
    parent=styles["detail-utc"],
    fontName="Times-Roman",
    fontSize=8.5,
    leftIndent=-5,
    rightIndent=10,
    spaceAfter=10,
    leading=12,
    alignment=TA_JUSTIFY,
)
styles["detail-mini-utc-center"] = ParagraphStyle(
    "detail-mini-utc-center",
    parent=styles["detail-utc"],
    fontName="Times-Roman",
    fontSize=8.5,
    leftIndent=-5,
    rightIndent=10,
    spaceAfter=10,
    leading=12,
    alignment=TA_CENTER,
)
styles["detail-mini-utc-tiny"] = ParagraphStyle(
    "detail-mini-utc-tiny",
    parent=styles["detail-utc"],
    fontName="Times-Roman",
    fontSize=4,
    leftIndent=0,
    rightIndent=0,
    spaceAfter=0,
    leading=2,
)
styles["detail-mini-overweight-cb"] = ParagraphStyle(
    "detail-mini-utc-tiny",
    parent=styles["detail-utc"],
    fontName="Times-Roman",
    fontSize=4,
    leftIndent=0,
    rightIndent=3,
    firstLineIndent=0,
    spaceAfter=2,
    leading=5,
)
styles["header"] = ParagraphStyle(
    "header", parent=styles["body"], fontSize=10, leading=16, leftIndent=0
)
styles["boxed"] = ParagraphStyle(
    "boxed",
    parent=styles["body"],
    borderWidth=1,
    borderPadding=3,
    borderColor=colors.black,
    alignment=TA_CENTER,
)
styles["heading-compact"] = ParagraphStyle(
    "heading-compact", parent=styles["heading"], spaceAfter=0, leading=12
)
styles["detail-compact"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    spaceAfter=0,
    leading=10,
    leftIndent=3,
    rightIndent=3,
)

styles["detail-compact-thp"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    fontSize=8,
    spaceAfter=0,
    leading=10,
    leftIndent=3,
    rightIndent=3,
)

styles["detail-compact-thp2"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    fontSize=7,
    spaceAfter=0,
    leading=6,
    leftIndent=-3,
    rightIndent=3,
)
styles["detail-compact-thp2-bold"] = ParagraphStyle(
    "detail-compact-thp2-bold-center",
    parent=styles["detail-compact-thp2"],
    fontName="Times-Bold",
)
styles["detail-compact-thp2-bold-center"] = ParagraphStyle(
    "detail-compact-thp2-bold-center",
    parent=styles["detail-compact-thp2"],
    fontName="Times-Bold",
    alignment=TA_CENTER,
)
styles["detail-compact-thp2-top"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    fontSize=7,
    spaceAfter=0,
    leading=6,
    leftIndent=-3,
    rightIndent=3,
    vAlign="TOP",
)
styles["detail-compact-thp2-right-skinny"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    fontSize=7,
    spaceAfter=0,
    leading=6,
    leftIndent=0,
    rightIndent=3,
    alignment=TA_RIGHT,
)
styles["detail-compact-thp3"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    fontSize=6,
    spaceAfter=0,
    leading=6,
    leftIndent=-3,
    rightIndent=3,
)
styles["detail-compact-thp3-space"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    fontSize=6,
    spaceAfter=2,
    leading=6,
    leftIndent=-3,
    rightIndent=3,
)

styles["detail-compact-thp3-right"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    fontSize=6,
    spaceAfter=0,
    leading=6,
    leftIndent=-3,
    rightIndent=3,
    alignment=TA_RIGHT,
)

styles["detail-compact-bold"] = ParagraphStyle(
    "detail-compact-bold",
    parent=styles["detail-utc"],
    spaceAfter=0,
    leading=10,
    leftIndent=3,
    rightIndent=3,
    alignment=TA_CENTER,
    fontName="Times-Bold",
)

styles["detail-flush"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    spaceBefore=0,
    spaceAfter=0,
    leading=11,
    leftIndent=0,
    rightIndent=0,
)
styles["detail-shrink"] = ParagraphStyle(
    "detail-flush", parent=styles["detail"], leading=10, fontSize=8
)

styles["sidebar"] = ParagraphStyle(
    "sidebar",
    parent=styles["detail"],
    fontName="Helvetica-Bold",
    spaceAfter=0,
    leading=10,
    leftIndent=0,
    rightIndent=0,
    backColor="black",
    textColor="white",
    alignment=TA_CENTER,
)
styles["trastop"] = ParagraphStyle(
    "trastop",
    parent=styles["detail-compact"],
    fontSize=8,
    leftIndent=0,
    rightIndent=0,
    spaceAfter=8,
)
styles["utt"] = ParagraphStyle(
    "bold",
    parent=styles["body"],
    # leading=18,
    textTransform="uppercase",
    # fontName='Times-Bold',
    # bulletFontName='Times-Bold',
    alignment=TA_CENTER,
    fontSize=7,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
    leading=0,
)
styles["utt_text"] = ParagraphStyle(
    "bold",
    parent=styles["body"],
    # leading=18,
    textTransform="uppercase",
    # fontName='Times-Bold',
    # bulletFontName='Times-Bold',
    alignment=TA_CENTER,
    fontSize=7,
    fontName="Helvetica",
    spaceBefore=0,
    spaceAfter=0,
    leading=0,
)
styles["rotated_detail"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-40,
    rightIndent=-20,
)
styles["rotated_detail_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-10,
    rightIndent=-20,
)


styles["rotated_detail_complaint"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-70,
    rightIndent=-20,
)


styles["rotated_detail_complaint_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-25,
    rightIndent=10,
    borderColor="#FF0000",
    borderWidth=1,
)

styles["rotated_detail_defendant"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-40,
    rightIndent=-10,
)

styles["rotated_detail_defendant_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-25,
    rightIndent=10,
    borderColor="#FF0000",
    borderWidth=1,
)

styles["rotated_detail_vehicle"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-47,
    rightIndent=-30,
)
styles["rotated_detail_vehicle_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-25,
    rightIndent=10,
    borderColor="#FF0000",
    borderWidth=1,
)
styles["rotated_detail_use_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-10,
    rightIndent=-10,
    borderColor="#FF0000",
    borderWidth=1,
)
styles["rotated_detail_violation"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-35,
    rightIndent=0,
)

styles["bullet"] = ListStyle(
    "list_default",
    leftIndent=20,
    rightIndent=0,
    spaceBefore=0,
    spaceAfter=5,
    bulletAlign="right",
    bulletType="bullet",
    bulletColor="black",
    bulletFontName="Helvetica",
    bulletFontSize=5,
    bulletOffsetY=-3,
    fontName="Times-Roman",
)

styles["rotated_detail_incident"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-25,
    rightIndent=0,
)


styles["rotated_detail_incident_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-25,
    rightIndent=10,
    borderColor="#FF0000",
    borderWidth=1,
)

styles["rotated_detail_bond"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-35,
    rightIndent=-5,
)

styles["rotated_detail_bond_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-25,
    rightIndent=10,
    borderColor="#FF0000",
    borderWidth=1,
)


styles["rotated_detail_courtplacedate"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-14,
    rightIndent=-6,
)
styles["rotated_detail_courtplacedate_ov"] = ParagraphStyle(
    "detail",
    parent=styles["detail-utc"],
    textColor="white",
    backColor="black",
    alignment=TA_CENTER,
    fontSize=8,
    leading=11,
    leftIndent=-25,
    rightIndent=10,
    borderColor="#FF0000",
    borderWidth=1,
)

styles["citation_table"] = TableStyle(
    [
        ("INNERGRID", (0, 0), (-1, -1), 0, colors.blue),
        ("BOX", (0, 0), (-1, -1), 0, colors.red),
    ]
)

styles["rc-divider-table"] = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), .45, "black"),
    ]
)

styles["rc-pdfdivider-table"] = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, -1), "#5f98f8"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
)

styles["citation_table_header"] = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, -1), colors.red),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("ALIGNMENT", (0, 0), (-1, -1), "CENTER"),
    ]
)

styles["detail-bold-center-large"] = ParagraphStyle(
    "detail",
    parent=styles["detail"],
    fontSize=12,
    fontName="Helvetica-Bold",
    alignment=TA_CENTER,
)

styles["detail-slimfit"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    spaceAfter=0,
    leading=10,
    leftIndent=-3,
    rightIndent=0,
)

styles["detail-slimfit-right"] = ParagraphStyle(
    "detail-compact",
    parent=styles["detail"],
    spaceAfter=0,
    leading=10,
    leftIndent=-3,
    rightIndent=0,
    alignment=TA_RIGHT,
)

# new style for ivap form main tables
styles["iv-main-table"] = TableStyle(
    [
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]
)


def extend_style(style, **params):
    return ParagraphStyle("extended", parent=style, **params)


def auto_span_table(table_list, **params):
    if "style" not in params:
        params["style"] = []
    spans = []
    for i, row in enumerate(table_list):
        span_start = 0
        span_end = 0
        for j, col in enumerate(row):
            if col is None:
                span_end += 1
            else:
                if span_start < span_end:
                    spans.append(("SPAN", (span_start, i), (span_end, i)))
                span_start = j
                span_end = j
        if span_start < span_end:
            spans.append(("SPAN", (span_start, i), (span_end, i)))
    params["style"] += spans
    return Table(table_list, **params)


black_line = flowables.HRFlowable(
    width="92%",
    color="black",
    thickness=1,
    lineCap="round",
    spaceBefore=0,
    spaceAfter=1,
    hAlign="CENTER",
    vAlign="BOTTOM",
    dash=None,
)
grey_line = flowables.HRFlowable(
    width="92%",
    thickness=1,
    lineCap="round",
    spaceBefore=1,
    spaceAfter=1,
    hAlign="CENTER",
    vAlign="BOTTOM",
    dash=None,
)
black_line_ul = flowables.HRFlowable(
    width="100%",
    color="black",
    thickness=0.5,
    lineCap="round",
    spaceBefore=0,
    spaceAfter=1,
    hAlign="CENTER",
    vAlign="BOTTOM",
    dash=None,
)

black_line_short = flowables.HRFlowable(
    width="70%",
    color="black",
    thickness=0.5,
    lineCap="round",
    spaceBefore=0,
    spaceAfter=1,
    hAlign="RIGHT",
    vAlign="BOTTOM",
    dash=None,
)

# space=Spacer(1,0.2*inch)

yes_box = "<img height='10' width='12' src='%s' />&nbsp;" % os.path.join(
    cur_path, "images", "crossbox.png"
)
no_box = "<img height='10' width='12' src='%s' />&nbsp;" % os.path.join(
    cur_path, "images", "box.png"
)


class PageNumCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_date()
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_date(self):
        import datetime

        dt = datetime.datetime.now().strftime("%m/%d/%Y")
        self.setFont("Times-Roman", 9)
        self.drawCentredString(200 * mm, 267 * mm, dt)

    def draw_page_number(self, page_count):
        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.setFont("Times-Roman", 9)
        self.drawCentredString(110 * mm, 6 * mm, page)


class OneDatePageNumCanvas(PageNumCanvas):
    def draw_date(self):
        if self._pageNumber == 1 or self._pageNumber == len(self.pages):
            PageNumCanvas.draw_date(self)


class RotatedPara(Paragraph):
    def draw(self):
        self.style = extend_style(
            self.style, spaceBefore=0, spaceAfter=-1 * self.style.fontSize
        )

        self.canv.saveState()

        textWidth = stringWidth(self.text, self.style.fontName, self.style.fontSize)
        textHeight = self.style.fontSize
        self.canv.translate(0, -textWidth + 1.5)
        self.canv.rotate(90)
        x, y = self.wrap(textWidth + 10, textHeight)
        self.canv.setStrokeColor(self.style.backColor)
        lw = 3
        self.canv.setLineWidth(lw)
        self.canv.line(
            x, y - textHeight - lw + 2, x - textWidth - 10, y - textHeight - lw + 2
        )
        Paragraph.draw(self)

        self.canv.restoreState()


# START ILLINOIS CITATION REPORT
pdfmetrics.registerFont(
    TTFont("LucidaType", os.path.join(cur_path, "fonts", "LucidaSansTypewriter.ttf"))
)
pdfmetrics.registerFont(
    TTFont(
        "LucidaType-Bold",
        os.path.join(cur_path, "fonts", "LucidaSansTypewriter-Bold.ttf"),
    )
)
pdfmetrics.registerFontFamily("LucidaType", normal="LucidaType", bold="LucidaType-Bold")


def extend_table_style(style, *params):
    return TableStyle(parent=style, *params)


styles["il-citation-main-table"] = TableStyle(
    [
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]
)
styles["il-citation-main-nt-table"] = TableStyle(
    [
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 0.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5 * mm),
    ]
)
styles["il-citation-main"] = ParagraphStyle(
    "il-citation-main",
    fontSize=6,
    leading=8,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
    wordWrap=None,
    alignment=TA_LEFT,
    fontName="Arial",
)
styles["il-citation-doc-header"] = ParagraphStyle(
    "il-citation-doc-header",
    parent=styles["il-citation-main"],
    fontSize=8,
    leading=10,
    fontName="Arial-Bold",
    alignment=TA_CENTER,
)
styles["il-citation-table-header"] = ParagraphStyle(
    "il-citation-table-header",
    parent=styles["il-citation-main"],
    spaceBefore=2,
    spaceAfter=2,
    leftIndent=1,
    rightIndent=1,
)
styles["il-citation-field-header"] = ParagraphStyle(
    "il-citation-field-header",
    fontName="Arial-Bold",
    fontSize=5.5,
    leading=6.5,
    leftIndent=0,
    rightIndent=0,
)
styles["il-citation-field-header-sm"] = ParagraphStyle(
    "il-citation-field-header-sm",
    parent=styles["il-citation-field-header"],
    fontSize=4.75,
    leading=5.75,
)
styles["il-citation-field-data"] = ParagraphStyle(
    "il-citation-field-header",
    fontName="Arial",
    fontSize=7,
    leading=8,
    leftIndent=0,
    rightIndent=0,
)
styles["il-citation-rotated"] = ParagraphStyle(
    "il-citation-rotated",
    parent=styles["il-citation-main"],
    textColor="white",
    alignment=TA_CENTER,
    fontName="Arial-Bold",
    fontSize=7.5,
    leading=0,
    leftIndent=0,
    rightIndent=0,
)
styles["il-citation-instructions"] = ParagraphStyle(
    "il-citation-instructions",
    parent=styles["il-citation-main"],
    alignment=TA_JUSTIFY,
    fontName="Arial",
    fontSize=6.5,
    leading=7.5,
    leftIndent=0,
    rightIndent=0,
)
styles["il-citation-instructions-header"] = ParagraphStyle(
    "il-citation-instructions-header",
    parent=styles["il-citation-instructions"],
    alignment=TA_CENTER,
    fontName="Arial-Bold",
)
styles["il-citation-main-nt"] = ParagraphStyle(
    "il-citation-main-nt",
    fontSize=6,
    leading=8,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
    wordWrap=None,
    alignment=TA_LEFT,
    fontName="LucidaType",
)
styles["il-citation-field-header-nt"] = ParagraphStyle(
    "il-citation-field-header-nt",
    parent=styles["il-citation-main-nt"],
    fontSize=7,
    leading=9,
)
styles["il-citation-field-header-nt-tiny"] = ParagraphStyle(
    "il-citation-field-header-nt-tiny",
    parent=styles["il-citation-field-header-nt"],
    fontSize=4.5,
    leading=5,
)
styles["il-citation-field-data-nt"] = ParagraphStyle(
    "il-citation-field-data-nt",
    parent=styles["il-citation-main-nt"],
    fontName="Times-Bold",
    fontSize=8,
    leading=10,
)
styles["il-citation-instructions-nt"] = ParagraphStyle(
    "il-citation-instructions-nt",
    parent=styles["il-citation-main-nt"],
    fontName="Times-Bold",
    fontSize=9,
    leading=12,
)
# END ILLINOIS CITATION REPORT

# START ROCKDALE COURT REPORT
styles["rc-main"] = ParagraphStyle(
    "rc-main",
    fontSize=10,
    leading=14,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
    wordWrap=None,
    alignment=TA_LEFT,
    fontName="Times-Roman",
)

styles["rc-doc-header"] = ParagraphStyle(
    "rc-doc-header",
    parent=styles["rc-main"],
    fontSize=12,
    leading=13.5,
    trailing=0,
    fontName="Times-Bold",
    alignment=TA_CENTER,
)
styles["rc-header"] = ParagraphStyle(
    "rc-main",
    parent=styles["rc-main"],
    fontSize=12,
    leading=13.5,
    trailing=0,
    fontName="Times-Bold",
    alignment=TA_CENTER,
)
styles["rc-section-header"] = ParagraphStyle(
    "rc-main",
    parent=styles["rc-main"],
    fontSize=12,
    leading=13.5,
    leftIndent=8.3 * mm,
    trailing=0,
    spaceBefore=4.3 * mm,
    spaceAfter=4.3 * mm,
    fontName="Times-Bold",
    alignment=TA_LEFT,
)
styles["rc-aawp-main"] = ParagraphStyle(
    "rc-aawp-main", parent=styles["rc-main"], fontSize=12, leading=13.7
)
styles["rc-fdo-main"] = ParagraphStyle(
    "rc-fdo-main", parent=styles["rc-main"], leading=11.5
)
styles["rc-fdo-doc-header"] = ParagraphStyle(
    "rc-fdo-doc-header",
    parent=styles["rc-main"],
    fontSize=10,
    leading=11.5,
    trailing=0,
    spaceBefore=10,
    spaceAfter=10,
    fontName="Times-Bold",
    alignment=TA_CENTER,
)
styles["rc-bw-main"] = ParagraphStyle(
    "rc-bw-main",
    parent=styles["rc-main"],
    fontSize=11,
    leading=11,
    fontName="LiberationSerif",
)
styles["rc-bw-doc-header"] = ParagraphStyle(
    "rc-bw-doc-header", parent=styles["rc-main"], fontSize=10, leading=11, trailing=0
)
styles["rc-bw-title"] = ParagraphStyle(
    "rc-bw-title",
    parent=styles["rc-bw-main"],
    fontSize=17,
    leading=17,
    trailing=0,
    alignment=TA_CENTER,
)
styles["rc-main-table"] = TableStyle(
    [
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]
)

styles["rc-square-table"] = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, 0), 4.5),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 5.5),
    ]
)

styles["rc-main-rmt"] = ParagraphStyle(
    "rc-main-rmt",
    fontSize=8,
    leading=9,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
    wordWrap=None,
    alignment=TA_LEFT,
    fontName="Arial",
)

styles["rc-main-1"] = ParagraphStyle(
    "rc-main-1",
    fontSize=8,
    leading=0,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
    wordWrap=None,
    fontName="Arial",
)

styles["rc-doc-header-rmt"] = ParagraphStyle(
    "rc-doc-header",
    parent=styles["rc-main"],
    fontSize=16,
    leading=32.5,
    leftIndent=7,
    trailing=0,
    fontName="Arial",
    alignment=TA_LEFT,
)

styles["rc-rmt-main"] = ParagraphStyle(
    "rc-rmt-main", parent=styles["rc-main-rmt"], leading=11.5
)
# END ROCKDALE COURT REPORT

styles["rc-table-first"] = ParagraphStyle(
    "rc-table-first",
    parent=styles["rc-main"],
    fontSize=9,
    leading=10,
    spaceBefore=0,
    spaceAfter=1,
    leftIndent=3.3 * mm,
    rightIndent=3.3 * mm,
    alignment=TA_LEFT,
)

styles["rc-main-para"] = ParagraphStyle(
    "rc-main-para",
    parent=styles["rc-main"],
    fontSize=12,
    spaceAfter=5,
    leftIndent=1.3 * mm,
    rightIndent=2.3 * mm,
    alignment=TA_LEFT,
)

styles["rc-big-para"] = ParagraphStyle(
    "rc-big-para",
    parent=styles["rc-main"],
    fontSize=11,
    spaceAfter=0,
    leading=10,
    leftIndent=0.8 * mm,
    alignment=TA_LEFT,
)

styles["rc-big-para1"] = ParagraphStyle(
    "rc-big-para1",
    parent=styles["rc-big-para"],
    leftIndent=4.8 * mm,
)

styles["rc-main-header"] = ParagraphStyle(
    "rc-main-header",
    parent=styles["rc-main"],
    fontSize=10,
    spaceBefore=5,
    leftIndent=1.3 * mm,
    fontName="Times-Bold",
    alignment=TA_CENTER,
)

styles["rc-table-border-coi"] = ParagraphStyle(
    "rc-table-border-coi",
    parent=styles["rc-main"],
    fontSize=9,
    spaceBefore=0,
    borderColor= '#000000',
    borderWidth=.45,
    leftIndent=0,
    fontName="Arial",
    alignment=TA_CENTER,
)

styles["rc-small-header"] = ParagraphStyle(
    "rc-small-header",
    parent=styles["rc-main-header"],
    fontSize=6,
    leading=5,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=1.3 * mm,
    fontName="Times-Bold",
    alignment=TA_LEFT,
)

styles["rc-small-content"] = ParagraphStyle(
    "rc-small-content",
    parent=styles["rc-small-header"],
    fontSize=5,
    leading=6,
    spaceAfter=0,
    fontName="Arial",
)

styles["rc-right-header"] = ParagraphStyle(
    "rc-right-header",
    parent=styles["rc-small-header"],
    fontSize=9,
    spaceAfter=0,
    leading=3,
    fontName="LiberationSerif",
)

styles["rc-medium-content"] = ParagraphStyle(
    "rc-medium-content",
    parent=styles["rc-small-header"],
    fontSize=9,
    leading=10,
    fontName="Arial",
)

styles["rc-white-text"] = ParagraphStyle(
    "rc-white-text",
    parent=styles["rc-medium-content"],
    textColor="white",
    fontSize=9,
    fontName="Arial-Bold",
)

styles["rc-blue-text"] = ParagraphStyle(
    "rc-blue-text",
    parent=styles["rc-medium-content"],
    textColor="#5f98f8",
    fontName="Arial-Bold",
    alignment=TA_CENTER
)

styles["rc-blue-text1"] = ParagraphStyle(
    "rc-blue-text1",
    parent=styles["rc-blue-text"],
    alignment=TA_LEFT
)


styles["rc-main-content"] = ParagraphStyle(
    "rc-main-content",
    parent=styles["rc-medium-content"],
    leftIndent=0.8*mm,
    alignment=TA_LEFT
)

styles["rc-long-content"] = ParagraphStyle(
    "rc-long-content",
    parent=styles["rc-main-content"],
    leading=16,
    fontSize=10,
    alignment=TA_JUSTIFY
)

styles["rc-medium-content-justify"] = ParagraphStyle(
    "rc-medium-content-justify",
    parent=styles["rc-medium-content"],
    alignment=TA_JUSTIFY
)

styles["rc-medium-content-center"] = ParagraphStyle(
    "rc-medium-content-center",
    parent=styles["rc-medium-content"],
    leftIndent=0,
    fontName="Arial",
    alignment=TA_CENTER,
)

styles["rc-medium-content-right"] = ParagraphStyle(
    "rc-medium-content-right",
    parent=styles["rc-medium-content"],
    leftIndent=0,
    fontName="Arial",
    alignment=TA_LEFT,
)

styles["rc-small-header-center"] = ParagraphStyle(
    "rc-small-header-center",
    parent=styles["rc-small-header"],
    leftIndent=0,
    alignment=TA_CENTER,
)

styles["rc-medium-header"] = ParagraphStyle(
    "rc-medium-header",
    parent=styles["rc-small-header"],
    leading=10,
    fontSize=9,
    leftIndent=1.3 * mm,
)

styles["rc-bold-header"] = ParagraphStyle(
    "rc-bold-header",
    parent=styles["rc-medium-header"],
    leading=15,
    textColor="#5f98f8",
    fontSize=12,
)

styles["rc-medium-header-underline"] = ParagraphStyle(
    "rc-medium-header-underline",
    parent=styles["rc-medium-header"],
    underlineWidth=10,
    underlineColor='black',
    alignment=TA_CENTER,
)

styles["rc-medium-header-center"] = ParagraphStyle(
    "rc-medium-header-center",
    parent=styles["rc-medium-header"],
    alignment=TA_CENTER,
)

styles["rc-medium-header-right"] = ParagraphStyle(
    "rc-medium-header-right",
    parent=styles["rc-medium-header"],
    alignment=TA_RIGHT,
)

styles["rc-my-doc-header"] = ParagraphStyle(
    "rc-my-doc-header",
    parent=styles["rc-main"],
    leading=22,
    fontSize=17,
    fontName="Times-Bold",
)

styles["rc-pdf-header"] = ParagraphStyle(
    "rc-pdf-header",
    parent=styles["rc-my-doc-header"],
    fontSize=22,
    textColor="#5f98f8",
    leading=12,
    fontName="Arial-Bold",
    alignment=TA_CENTER,
)

styles["rc-nico-header"] = ParagraphStyle(
    "rc-nico-header",
    parent=styles["rc-my-doc-header"],
    fontSize=22,
    leading=12,
    fontName="Arial-Bold"
)

styles["rc-my-doc-header-subtitle"] = ParagraphStyle(
    "rc-my-doc-header-subtitle",
    parent=styles["rc-my-doc-header"],
    fontSize=14,
    alignment=TA_CENTER,
    leftIndent=3.3 * mm,
    backColor="#d1d1d1"
)

styles["rc-first-label"] = ParagraphStyle(
    "rc-first-label",
    parent=styles["rc-small-header"],
    fontSize=8,
    leading=10,
    leftIndent=1.6 * mm,
    rightIndent=.1 * mm,
    fontName="Arial",
)

styles["rc-normal-text"] = ParagraphStyle(
    "rc-normal-text",
    parent=styles["rc-small-header"],
    leading=10,
    fontSize=8,
    justifyBreaks=0,
    fontName="Arial",
)

styles["rc-bold-text"] = ParagraphStyle(
    "rc-bold-text",
    parent=styles["rc-normal-text"],
    fontName="Arial-Bold",
    leading=9,
    alignment=TA_LEFT,
)

styles["rc-bold-text-underline"] = ParagraphStyle(
    "rc-bold-text-underline",
    parent=styles["rc-bold-text"],
    underlineWidth=1,
    underlineColor='black'
)

styles["rc-normal-center"] = ParagraphStyle(
    "rc-normal-center",
    parent=styles["rc-normal-text"],
    leading=9,
    leftIndent=0,
    alignment=TA_CENTER,
)

styles["rc-bold-center"] = ParagraphStyle(
    "rc-bold-center",
    parent=styles["rc-normal-center"],
    leading=9,
    fontName="Arial-Bold",
)

styles["rc-normal-end"] = ParagraphStyle(
    "rc-normal-end",
    parent=styles["rc-normal-text"],
    alignment=TA_RIGHT,
)

styles["rc-checkbox-text"] = ParagraphStyle(
    "rc-checkbox-text",
    parent=styles["rc-small-header"],
    fontSize=8,
    leading=10,
    leftIndent=1.8 * mm,
    fontName="Arial",
)

styles["rc-checkbox-text-small"] = ParagraphStyle(
    "rc-checkbox-text-small",
    parent=styles["rc-checkbox-text"],
    leftIndent=1*mm,
)

styles["rc-divider-text"] = ParagraphStyle(
    "rc-divider-text",
    parent=styles["rc-my-doc-header"],
    fontSize=10,
    leading=12,
    alignment=TA_LEFT,
    leftIndent=1.0 * mm,
)

styles["rc-normal-header"] = ParagraphStyle(
    "rc-normal-header",
    parent=styles["rc-small-header"],
    leading=11,
    fontSize=10,
)

styles["rc-normal-header1"] = ParagraphStyle(
    "rc-normal-header",
    parent=styles["rc-small-header"],
    leading=11,
    fontSize=9,
)

styles["rc-normal-text1"] = ParagraphStyle(
    "rc-normal-text1",
    parent=styles["rc-normal-text"],
    leading=11,
    firstLineIndent=13,
    fontSize=9,
    fontName="Arial",
    alignment=TA_JUSTIFY,
)

styles["rc-header-text"] = ParagraphStyle(
    "rc-header-text",
    parent=styles["rc-normal-header"],
    leading=12,
    fontSize=12,
    alignment=TA_CENTER,
)

styles["rc-small-underline"] = ParagraphStyle(
    "rc-small-underline",
    parent=styles["rc-small-content"],
    fontSize=6,
    firstLineIndent=0,
    spaceBefore=0,
    leftIndent=0,
    spaceAfter=0,
    leading=0,
)

styles["rc-underline-text"] = ParagraphStyle(
    "rc-underline-text",
    parent=styles["rc-small-content"],
    leading=0,
)

styles["rc-underline-text1"] = ParagraphStyle(
    "rc-underline-text1",
    parent=styles["rc-medium-content"],
    leading=16,
)