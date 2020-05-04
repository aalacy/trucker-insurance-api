# -*- coding: utf-8 -*-
import cStringIO
from datetime import datetime as date
import json

from document_specific_styles import *
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Flowable, Paragraph, Table, Spacer

L_S = 2.2 

def nico(title='nico.pdf', author=None, name="", address="", policy="{}"):
    cr =ROCReport(title, author, name, address, policy)
    buff = cStringIO.StringIO()
    return cr.create_report(buff)

class ROCReport:
    BASE_PATH = os.path.abspath(os.curdir) + '/routes/coi'

    def __init__(self, title=None, author=None, name="", address="", policy=None):
        self.page_size = letter
        self.page_margin = (7 * mm, 6.4 * mm)
        self.sections = ["header", "content"]
        self.title = title
        self.author = author
        self.name = name or ""
        self.address = address or ""
        self.policy = json.loads(policy) if policy else {}

    def validate(self, val):
        if val:
            return val.strip()
        else:
            return ""

    def create_report(self, buff=None):
        def get_method(section):
            try:
                method = getattr(self, "_section_" + section)
            except AttributeError:
                raise Exception("Section method not found: " + section)
            return method
        
        if not buff:
            buff = io.BytesIO()

        story = []
        for section in self.sections:
            elems = get_method(section)()
            for elem in elems:
                story.append(elem)

        page_t = PageTemplate('normal', [
            Frame(
                self.page_margin[0],
                self.page_margin[1],
                self.page_size[0] - self.page_margin[0] * 2,
                self.page_size[1] - self.page_margin[1] * 2,
                leftPadding=0,
                bottomPadding=self.page_margin[0],
                rightPadding=0,
                topPadding=self.page_margin[0] / 5,
            )
        ])
        doc_t = BaseDocTemplate(
            buff,
            pagesize=letter,
            title=self.title,
            author=self.author,
            leftMargin=self.page_margin[0],
            rightMargin=self.page_margin[0],
            topMargin=self.page_margin[1],
            bottomMargin=self.page_margin[1],
        )
        doc_t.addPageTemplates(page_t)
        doc_t.build(story)

        buff.seek(0)
        return buff

    def _section_header(self):        
        elems = list()
        elems += [
            Table(
                [
                    [
                        Table(
                            [
                                [
                                    Paragraph(
                                        "Truck Application",                
                                        extend_style(styles["rc-nico-header"])
                                    ),
                                ],
                                [
                                    Paragraph(
                                        "COLUMBIA INSURANCE COMPANY <br />NATIONAL INDEMNITY COMPANY<br/> NATIONAL FIRE & MARINE INSURANCE COMPANY<br/>NATIONAL LIABILITY & FIRE INSURANCE COMPANY<br/>NATIONAL INDEMNITY COMPANY OF THE SOUTH<br/>NATIONAL INDEMNITY COMPANY OF MID-AMERICA",                
                                        extend_style(styles["rc-medium-header"])
                                    ),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("TOPPADDING", (0, 0), (-1, -1), 25),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 80),
                            ])
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                        ]),
                rowHeights=32.4 * mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("Policy Term From:", extend_style(styles["rc-first-label"])),
                        Table(
                            [
                                [ 
                                    Paragraph("", styles["rc-small-content"]),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("LINEBELOW", (0, 0), (-1, -1), .45, "black"),
                            ]),
                        )
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]),
                colWidths=( 100 * mm, 25 * mm, 76 * mm),
            ),
        ]
            
        return elems

    def checkbox(self, checked=None, size='medium'):
        x = ''
        if checked:
            x = 'X'
        width = 5.8
        height = 5.2
        if size == 'small':
            width = 2.5
            height = 2.5
        return Table(
            [
                [   
                    Paragraph("{}".format(x), styles["rc-medium-content-center"]),
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), .45, "black"),
            ]),
            colWidths=(width*mm),
            rowHeights=(height*mm)
        )

    def yes_no(self):
        return Table(
            [
                [
                    self.checkbox(size='small'),
                    Paragraph("Yes", styles["rc-checkbox-text-small"]),
                    self.checkbox(size='small'),
                    Paragraph("No", styles["rc-checkbox-text-small"]),
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]),
            colWidths=(3*mm, 8*mm, 3*mm, 7*mm),
        )

    def checkbox_text(self, text, width, bold=False):
        text_style = "rc-checkbox-text-small"
        if bold:
            text_style = "rc-bold-text"
        return Table(
            [
                [
                    self.checkbox(size='small'),
                    Paragraph(text, styles[text_style]),
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]),
            colWidths=(3*mm, width*mm),
        )

    def right_header(self, number):
        return Table(
                [
                    [   
                        Paragraph(number, extend_style(styles["rc-medium-content-right"]))
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),

                ]),
                colWidths=( 5*mm ),
            )

    def line_spacer(self):
        return [
            Table(
                [
                    [ 
                        Paragraph("", styles["rc-small-content"]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
            ),
        ]

    def underline(self):
        return  Table(
                    [
                        [ 
                            Paragraph("", styles["rc-small-content"]),
                        ]
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LINEBELOW", (0, 0), (-1, -1), .45, "black"),
                    ]),
                )

    def driver_information(self, number):
        return Table(
                [
                    [   
                       Paragraph(number, extend_style(styles["rc-normal-header"])),
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .15, "black"),
                ]),
                colWidths=(60*mm, 20*mm, 10*mm, 39*mm, 20*mm, 25*mm, 20*mm, 8*mm),
                rowHeights=4*mm
            ),

    def driver_information_continued(self, number):
        return Table(
                [
                    [   
                       Paragraph(number, extend_style(styles["rc-normal-header"])),
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(20*mm, 22*mm, 17*mm, 22*mm, 17*mm, 22*mm, 40*mm, 20*mm, 22*mm),
                rowHeights=4.5*mm
            ),

    def schedule_detail(self, number):
        return Table(
                [
                    [   
                       Paragraph(number, extend_style(styles["rc-normal-header"])),
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(7*mm, 9*mm, 22*mm, 18*mm, 52*mm, 18*mm, 9*mm, 30*mm, 10*mm, 15*mm, 12*mm),
                rowHeights=4.5*mm
            ),

    def physical_detail(self, number):
        return Table(
                [
                    [   
                        Paragraph(number, extend_style(styles["rc-normal-header"])),
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .25, "black"),
                ]),
                colWidths=(8*mm, 21*mm, 21*mm, 32*mm, 32*mm, 22*mm, 27*mm, 19*mm, 20*mm),
                rowHeights=4.7*mm
            ),

    def loss_experience(self):
        return Table(
                [
                    [   
                        Paragraph(" /&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/  ", extend_style(styles["rc-normal-center"])),
                        Paragraph(" /&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/  ", extend_style(styles["rc-normal-center"])),
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .25, "black"),
                ]),
                colWidths=(17.5*mm, 17.5*mm, 38*mm, 20*mm, 16*mm, 17.5*mm, 17.5*mm, 14.5*mm, 14.5*mm, 14.5*mm, 14.5*mm),
                rowHeights=5*mm
            ),

    def cargo_information(self):
        return Table(
                [
                    [   
                        Paragraph(" /&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/  ", extend_style(styles["rc-normal-center"])),
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .25, "black"),
                ]),
                colWidths=(17.5*mm, 17.5*mm, 48*mm, 20*mm, 16*mm, 35*mm, 23*mm, 25*mm),
                rowHeights=4*mm
            ),

    def describe_cargo(self):
        return  Table(
                    [
                        [   
                            None,
                            None,
                            None,
                            None,
                        ],
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("GRID", (0, 0), (-1, -1), .25, "black"),
                    ]),
                    colWidths=(80*mm, 24*mm, 24*mm, 24*mm),
                    rowHeights=5*mm
                ),

    def unisured_motorist_coverage(self):
        return  Table(
                    [
                        [
                            Paragraph("UNINSURED MOTORIST COVERAGE", extend_style(styles["rc-normal-center"])),
                        ],
                        [
                            Table(
                                [
                                    [
                                        Paragraph("Single Limit", extend_style(styles["rc-normal-center"])),
                                        Table(
                                            [
                                                [
                                                    Paragraph("Split Limits", extend_style(styles["rc-normal-center"])),
                                                ],
                                                [
                                                    Paragraph("Bodily Injury", extend_style(styles["rc-normal-center"])),
                                                ],
                                                [
                                                    Table(
                                                        [
                                                            [
                                                                Table(
                                                                    [
                                                                        [
                                                                            Paragraph("Per Person", extend_style(styles["rc-normal-center"])),
                                                                            Paragraph("Per Accident", extend_style(styles["rc-normal-center"])),
                                                                        ]
                                                                    ],
                                                                    style=extend_table_style(styles["rc-main-table"], [
                                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                                    ]),
                                                                    rowHeights=(4*mm)
                                                                ),
                                                            ]
                                                        ],
                                                        style=extend_table_style(styles["rc-main-table"], [
                                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                        ]),
                                                        rowHeights=(4*mm)
                                                    ),
                                                ]
                                            ],
                                            style=extend_table_style(styles["rc-main-table"], [
                                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                                            ]),
                                            rowHeights=(4*mm)
                                        ),
                                    ]
                                ],
                                style=extend_table_style(styles["rc-main-table"], [
                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                    ("LINEAFTER", (0, 0), (0, -1), .45, "black"),
                                ]),
                                colWidths=(33*mm, 50*mm),
                                rowHeights=(12*mm)
                            ),
                        ],
                        [
                            Table(
                                [
                                    [
                                        None,
                                        None,
                                        None,
                                    ]
                                ],
                                style=extend_table_style(styles["rc-main-table"], [
                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                    ("LINEAFTER", (0, 0), (0, -1), .45, "black"),
                                    ("LINEAFTER", (0, 0), (1, -1), .45, "black"),
                                    ("LINEAFTER", (0, 0), (2, -1), .45, "black"),
                                ]),
                                colWidths=(33*mm, 25*mm, 25*mm),
                                rowHeights=(4*mm)
                            ),
                        ]
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                    ]),
                    colWidths=(83*mm),
                    rowHeights=(4*mm, 12*mm, 4*mm)
                ),

    def _section_content(self):        
        elems = [
            Table(
                [
                    [   
                        self.right_header("1."),
                        Paragraph('Name (and "dba")', extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 5 * mm, 25 * mm, 172 * mm),
            ),
            Table(
                [
                    [   
                        None,
                        self.checkbox(size='small'),
                        Paragraph("Indivisual / Proprietorship", styles["rc-checkbox-text-small"]),
                        self.checkbox(size='small'),
                        Paragraph("Partnership", styles["rc-checkbox-text-small"]),
                        self.checkbox(size='small'),
                        Paragraph("Corporation", styles["rc-checkbox-text-small"]),
                        self.checkbox(size='small'),
                        Paragraph("Other", styles["rc-checkbox-text-small"]),
                        Paragraph("Business Phone Number", extend_style(styles["rc-first-label"])),
                        Table(
                            [
                                [ 
                                    self.underline()
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                ("TOPPADDING", (0, 0), (-1, -1), 1.5*L_S),
                            ]),
                            colWidths=57*mm,
                            rowHeights=3*mm,
                        )
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.5*L_S),
                ]),
                colWidths=(4*mm, 3*mm, 34*mm, 3*mm, 17*mm, 3*mm, 17*mm, 3*mm, 26*mm, 35*mm, 57*mm),
            ),
        ]  

        elems += [
            Table(
                [
                    [   
                        self.right_header("2."),
                        Paragraph("Mailing Address", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("City", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("State", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Zip", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 23 * mm, 78 * mm, 8*mm, 40*mm, 9*mm, 16*mm, 7*mm, 16*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("3."),
                        Paragraph("Premises Address", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("City", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("State", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Zip", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 26 * mm, 75 * mm, 8*mm, 40*mm, 9*mm, 16*mm, 7*mm, 16*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("4."),
                        Paragraph("Person to contact for inspection (name and phone number)", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 76 * mm, 121 * mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("5."),
                        Paragraph("Have you ever had insurance with one of the companies listed at the top of this page?", styles["rc-checkbox-text"]),
                        self.yes_no(),
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=(5*mm, 110*mm, 25*mm, 62*mm),
            ),
            Table(
                [
                    [   
                        None,
                        Paragraph("If yes, Policy Number(s)", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Effective Date(s)", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 33*mm, 85 * mm, 25*mm, 54* mm),
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("DESCRIPTION OF OPERATIONS", styles["rc-divider-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-divider-table"], [
                ]),
                rowHeights=(4*mm),
                colWidths=(204*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("6."),
                        Paragraph("Descibe business", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 25 * mm, 172 * mm),
            ),
            Table(
                [
                    [   
                        None,
                        Paragraph("Years experience", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("New Venture? ", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If you are a tow truck operation, do you do repossessions?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 24 * mm, 24 * mm, 24*mm, 21*mm, 78*mm, 21*mm, 5*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("7."),
                        Paragraph("Is this your primary business?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If no, explain", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 42 * mm, 25*mm, 20*mm, 110 * mm),
            ),
            Table(
                [
                    [   
                        None,
                        Paragraph("Seasonal?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 18 * mm, 21*mm, 158*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("8."),
                        Paragraph("Have you ever filed for bankruptcy?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, when", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Explain", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 48 * mm, 25*mm, 18*mm, 15*mm, 13*mm, 78*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("9."),
                        Paragraph("Gross receipts last year", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Estimate for coming year", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Business for sale?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 32 * mm, 38*mm, 34*mm, 32*mm, 27*mm, 25*mm, 9*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("10."),
                        Paragraph("Do you operate in more than one state?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, list states", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 52 * mm, 25*mm, 27*mm, 92*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("11."),
                        Paragraph("Do you haul for hire?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("Show largest cities entered", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 32 * mm, 25*mm, 38*mm, 101*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("12."),
                        Paragraph("Do you operate over a regular route?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, show towns operated between", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 52 * mm, 25*mm, 50*mm, 69*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("13."),
                        Paragraph("Are you a common carrier?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("Are you a contract hauler?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, for whom", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 38 * mm, 25*mm, 38 * mm, 25*mm, 25*mm, 45*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("14."),
                        Paragraph("List all types of cargo hauled", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 40 * mm, 156*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("15."),
                        Paragraph("Do you haul any hazardous or extra hazardous substances or materials as defined by EPA?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, provide the complete listing", extend_style(styles["rc-first-label"])),
                       
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 120 * mm, 25*mm, 51*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("identifying all materials(s) and/or chemical content:", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 66 * mm, 130*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("16."),
                        Paragraph("Do you haul your cargo exclusively?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If not, who owns it?", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 49*mm, 25*mm, 28*mm, 94*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("17."),
                        Paragraph("Do you pull double trailer?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("Triple trailer?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 37*mm, 25*mm, 21*mm, 113*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("18."),
                        Paragraph("Do you rent or lease your vehicles to others?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, attach copy of rental or lease agreement form uses.", extend_style(styles["rc-first-label"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 59*mm, 25*mm, 112*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("19."),
                        Paragraph("Do you hire any vehicles?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("Complete Hired and Non-Owned Supplemental Questionnaire if coverage is desired.", extend_style(styles["rc-first-label"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 36*mm, 25*mm, 135*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("LIABILITY COVERAGE", extend_style(styles["rc-normal-header"])),
                       Paragraph("-", extend_style(styles["rc-bold-text"])),
                       Paragraph("Complete for desired coverages by indicating limits of insurance.", extend_style(styles["rc-bold-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(43*mm, 3*mm, 156*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [  
                        Table(
                            [
                                [
                                    Paragraph("LIABILITY", extend_style(styles["rc-normal-center"])),
                                ],
                                [
                                    Table(
                                        [
                                            [
                                                Paragraph("Combined Single <br /> Limit BI & PD", extend_style(styles["rc-normal-center"])),
                                                Table(
                                                    [
                                                        [
                                                            Paragraph("Split Limits", extend_style(styles["rc-normal-center"])),
                                                        ],
                                                        [
                                                            Table(
                                                                [
                                                                    [
                                                                        Paragraph("Bodily Injury", extend_style(styles["rc-normal-center"])),
                                                                        Paragraph("Property <br /> Damage", extend_style(styles["rc-normal-center"])),
                                                                    ]
                                                                ],
                                                                style=extend_table_style(styles["rc-main-table"], [
                                                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                                ]),
                                                                colWidths=(40*mm, 20*mm),
                                                                rowHeights=(8*mm)
                                                            ),
                                                        ],
                                                        [
                                                            Table(
                                                                [
                                                                    [
                                                                        Table(
                                                                            [
                                                                                [
                                                                                    Paragraph("Per Person", extend_style(styles["rc-normal-center"])),
                                                                                    Paragraph("Per Accident", extend_style(styles["rc-normal-center"])),
                                                                                    Paragraph("Per Accident", extend_style(styles["rc-normal-center"])),
                                                                                ]
                                                                            ],
                                                                            style=extend_table_style(styles["rc-main-table"], [
                                                                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                                            ]),
                                                                            rowHeights=(4*mm)
                                                                        ),
                                                                    ]
                                                                ],
                                                                style=extend_table_style(styles["rc-main-table"], [
                                                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                                ]),
                                                                rowHeights=(4*mm)
                                                            ),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    rowHeights=(4*mm, 8*mm, 4*mm)
                                                ),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("LINEAFTER", (0, 0), (0, -1), .45, "black"),
                                        ]),
                                        colWidths=(41*mm, 60*mm),
                                        rowHeights=(16*mm)
                                    ),
                                ],
                                [
                                    Table(
                                        [
                                            [
                                                None,
                                                None,
                                                None,
                                                None,
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("LINEAFTER", (0, 0), (0, -1), .45, "black"),
                                            ("LINEAFTER", (0, 0), (1, -1), .45, "black"),
                                            ("LINEAFTER", (0, 0), (2, -1), .45, "black"),
                                        ]),
                                        colWidths=(41*mm, 20*mm, 20*mm, 20*mm),
                                        rowHeights=(4*mm)
                                    ),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(101*mm),
                            rowHeights=(4*mm, 16*mm, 4*mm)
                        ),
                        Table(
                            [
                                [
                                    Table(
                                        [
                                            [
                                                Table(
                                                    [
                                                        [
                                                            Paragraph("Medical Payments", extend_style(styles["rc-normal-center"])),
                                                        ],
                                                        [
                                                            None
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    rowHeights=(20*mm, 4*mm)
                                                ),
                                                Table(
                                                    [
                                                        [
                                                            Paragraph("Personal <br /> Injury <br /> Projection <br /> (where <br /> applicable)", extend_style(styles["rc-normal-center"])),
                                                        ],
                                                        [
                                                            None
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    rowHeights=(20*mm, 4*mm)
                                                )
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        colWidths=(18*mm, 18*mm),
                                        rowHeights=(24*mm)
                                    ),
                                    Paragraph("IF PHYSICAL DAMAGE COVERAGE DESIRED, <br /> REFER TO FOLLOWING PAGE. <br /><br /> IF IN TOW COVERAGE DESIRED, <br /> COMPLETE TOW TRUCK SUPPLEMENT. <br /><br /> HIRED, NON-OWNED - M-4055.", extend_style(styles["rc-bold-text"])),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ]),
                            colWidths=(36*mm, 65*mm),
                            rowHeights=(24*mm)
                        )
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]),
                rowHeights=(24*mm)
            )
        ]

        elems += self.line_spacer()
        elems += self.line_spacer()

        elems += [
            Table(
                [
                    [   
                        self.unisured_motorist_coverage(),
                        None,
                        self.unisured_motorist_coverage()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                ]),
                colWidths=(83*mm, 36*mm, 83*mm),
                rowHeights=20*mm
            ),
        ]

        elems += self.line_spacer()
        elems += self.line_spacer()

        elems += [
            Table(
                [
                    [   
                       Paragraph("Driver Information", extend_style(styles["rc-normal-header"])),
                       Paragraph("-", extend_style(styles["rc-bold-text"])),
                       Paragraph("If additional space is needed, attach seperate listing.", extend_style(styles["rc-bold-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(32*mm, 3*mm, 167*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [   
                    [
                        Table(
                            [
                                [   
                                    Paragraph("Driver's Name", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Date of Birth", extend_style(styles["rc-normal-center"])),
                                    Table(
                                        [
                                            [   
                                                Table(
                                                    [
                                                        [   
                                                           Paragraph("Driver's License", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Experience", extend_style(styles["rc-normal-center"])),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    colWidths=(94*mm, 28*mm),
                                                    rowHeights=4*mm
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                           Paragraph("State", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Number", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Class Type <br /> (i.e CDL)", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Years<br/> Licensed (In<br/> Class/Type)", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Type of Unit<br/>(Bus, Van,<br/>Truck,<br/>Tractor, etc.)", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("No.<br/> of<br/>Years", extend_style(styles["rc-normal-center"])),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    colWidths=(10*mm, 39*mm, 20*mm, 25*mm, 20*mm, 8*mm),
                                                    rowHeights=14*mm
                                                ),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        colWidths=(122*mm),
                                        rowHeights=(4*mm, 14*mm)
                                    ),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(60*mm, 20*mm, 122*mm),
                            rowHeights=18*mm
                        ),
                    ],
                    [   
                        self.driver_information('1.')
                    ],
                    [   
                        self.driver_information('2.')
                    ],
                    [   
                        self.driver_information('3.')
                    ],
                    [   
                        self.driver_information('4.')
                    ],
                    [   
                        self.driver_information('5.')
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(18*mm, 4*mm, 4*mm, 4*mm, 4*mm, 4*mm) 
            ),
        ]

        # 1 page footer
        elems += [
            Table(
                [
                    [   
                       Paragraph("M-4467d VA (12/2007)", extend_style(styles["rc-bold-text"])),
                       Paragraph("Truck Application Page 1 of 5", extend_style(styles["rc-normal-end"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                ]),
                colWidths=(90*mm, 112*mm),
                rowHeights=6*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("Driver Information", extend_style(styles["rc-normal-header"])),
                       Paragraph("(Continued) - If additional space is needed, attach seperate listing.", extend_style(styles["rc-bold-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(31*mm, 171*mm),
                rowHeights=6*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("No. Years<br/>Previous<br/>Commercial<br/>Driving<br/>Experience", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Date of Hire", extend_style(styles["rc-normal-center"])),
                                    Table(
                                        [
                                            [   
                                                Paragraph("Accidents and Minor Moving Traffic <br/> Violations in Past 5 Years", extend_style(styles["rc-normal-center"])),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                           Paragraph("No. of<br/> Accidents", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Date(s)", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("No. of<br/> Violations", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Date(s)", extend_style(styles["rc-normal-center"])),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    colWidths=(17*mm, 22*mm, 17*mm, 22*mm),
                                                    rowHeights=(7*mm)
                                                ),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        rowHeights=(15*mm, 7*mm)
                                    ),
                                    Table(
                                        [
                                            [   
                                                Paragraph("Major Convictions<br/>(DWI/DUI, Hit & Run, Manslaughter, Rechless, <br/>Driving While Suspended/ Revoked, Speed<br/> Contest, other felony)", extend_style(styles["rc-normal-center"])),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                           Paragraph("Describe Conviction", extend_style(styles["rc-normal-center"])),
                                                           Paragraph("Date(s)", extend_style(styles["rc-normal-center"])),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    colWidths=(40*mm, 20*mm),
                                                    rowHeights=(7*mm)
                                                ),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        rowHeights=(15*mm, 7*mm)
                                    ),
                                    Paragraph("Employee (E)<br/>Ind Cont. (IC)<br/>Owner/Op. (O/O)<br/>Franchisee (F)<br/>", extend_style(styles["rc-normal-center"])),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(20*mm, 22*mm, 78*mm, 60*mm, 22*mm),
                            rowHeights=22*mm
                        ),
                    ],
                    [
                        self.driver_information_continued("1.")
                    ],
                    [
                        self.driver_information_continued("2.")
                    ],
                    [
                        self.driver_information_continued("3.")
                    ],
                    [
                        self.driver_information_continued("4.")
                    ],
                    [
                        self.driver_information_continued("5.")
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(22*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("PLEASE ATTACH DETAILED EXPLANATION OF ACCIDENTS LISTED ABOVE", extend_style(styles["rc-medium-header"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=(202*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("20."),
                        Paragraph("Are drivers covered by Workers Compensation?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, name of carrier?", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 66*mm, 25*mm, 32*mm, 73*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("21."),
                        Paragraph("Minimum years driving experience required", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        None,
                        Paragraph("Are vehicles owner-driven only?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 58*mm, 25*mm, 20*mm, 45*mm, 48*mm ),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("22."),
                        Paragraph("Are drivers ever allowed to take vehicles home at night?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, will family members drive?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 73*mm, 30*mm, 46*mm, 47*mm ),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("23."),
                        Paragraph("Do you order MVR's on all drivers prior to hiring?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("Drivers maximum driving hours", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("daily,", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("weekly", extend_style(styles["rc-first-label"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 73*mm, 30*mm, 42*mm, 10*mm, 10*mm, 10*mm, 21*mm ),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("24."),
                        Paragraph("Do you agree to report all newly hired operators?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 73*mm, 123*mm ),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("25."),
                        Paragraph("What is the basis for driver(s) pay?", extend_style(styles["rc-first-label"])),
                        self.checkbox_text("Hourly", 17),
                        self.checkbox_text("Trip", 11),
                        self.checkbox_text("Mileage", 25),
                        self.checkbox_text("Other,", 12),
                        Paragraph("Explain", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 56*mm, 17*mm, 11*mm, 25*mm, 12*mm, 13*mm, 62*mm ),
                rowHeights=6*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("SCHEDULE OF AUTOS/VEHICLES", extend_style(styles["rc-normal-header"])),
                       Paragraph("- Describe all the vehicles for which application is made for insurance", extend_style(styles["rc-bold-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(60*mm, 142*mm),
                rowHeights=6*mm
            ),
        ]

        elems += [
            Table(
                [   
                    [   
                        Table(
                            [
                                [   
                                   Paragraph("Veh.<br/>No.", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Model<br/>Year", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Vehicle Make<br/>& Model", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Body Type<br/>Truck,<br/>Tructor,<br/>Trailer, etc.)", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Full Vehicle Identification<br/>Number", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Gross<br/>Vehicle<br/>Weight<br/>GVW", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Total<br/># of<br/>Rear<br/>Axles", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Principal Garaging<br/>Location<br/>(city & state)", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Radius<br/>of<br/>Opera-<br/>tion", extend_style(styles["rc-normal-center"])),
                                   Paragraph("Annual<br/>Mileage<br/>Per<br/>Vehicle", extend_style(styles["rc-normal-center"])),
                                   Paragraph("(A) Anti-<br/>Lock<br/>Brakes,<br/>(B) Air<br/>Bags", extend_style(styles["rc-normal-center"])),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(7*mm, 9*mm, 22*mm, 18*mm, 52*mm, 18*mm, 9*mm, 30*mm, 10*mm, 15*mm, 12*mm),
                            rowHeights=(18*mm)
                        ),
                    ],
                    [   
                        self.schedule_detail("1."),
                    ],
                    [   
                        self.schedule_detail("2."),
                    ],
                    [   
                        self.schedule_detail("3."),
                    ],
                    [   
                        self.schedule_detail("4."),
                    ],
                    [   
                        self.schedule_detail("5."),
                    ],
                    [   
                        self.schedule_detail("6."),
                    ],
                    [   
                        self.schedule_detail("7."),
                    ],
                    [   
                        self.schedule_detail("8."),
                    ],
                    [   
                        self.schedule_detail("9."),
                    ],
                    [   
                        self.schedule_detail("10."),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(18*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm, 4.5*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("26."),
                        Paragraph("Will lessor be added as additional insured?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, give me name and address of lessor of each vehicle", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2*L_S),
                ]),
                colWidths=( 6*mm, 57*mm, 25*mm, 77*mm, 37*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 7*mm, 195*mm ),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("27."),
                        Paragraph("Number of vehicles owned:", extend_style(styles["rc-first-label"])),
                        Paragraph("Pick-Ups", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Trucks", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Tractors", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Semi-Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Pup Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 36*mm, 13*mm, 12*mm, 11*mm, 12*mm, 13*mm, 12*mm, 19*mm, 12*mm, 12*mm, 12*mm, 18*mm, 14*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("28."),
                        Paragraph("Number of vehicles leased:", extend_style(styles["rc-first-label"])),
                        Paragraph("Pick-Ups", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Trucks", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Tractors", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Semi-Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("Pup-Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2*L_S),
                ]),
                colWidths=( 6*mm, 36*mm, 13*mm, 12*mm, 11*mm, 12*mm, 13*mm, 12*mm, 19*mm, 12*mm, 12*mm, 12*mm, 18*mm, 14*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("PHYSICAL DAMAGE COVERAGE", extend_style(styles["rc-normal-header"])),
                       Paragraph("- Complete spaces below in detail for each respective auto/vehicle described above.", extend_style(styles["rc-bold-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(58*mm, 144*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [   
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("Veh.<br/>No.", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Date<br/>Published", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Cost When<br/>Purchased", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Current Stated Value<br/>(Excluding permanently<br/>attached equipment)", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Value of Permanently<br/>Attached Special<br/>Equipment", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Total Stated<br/>Amount to be<br/>Insured", extend_style(styles["rc-normal-center"])),
                                    Table(
                                        [
                                            [   
                                                Paragraph("Physical Damage Deductible", extend_style(styles["rc-normal-center"])),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            Table(
                                                                [
                                                                    [   
                                                                       None, 
                                                                       self.checkbox_text("Comprehensive", 24)
                                                                    ],
                                                                    [
                                                                       None,
                                                                       self.checkbox_text("Spec. C of Loss", 24)
                                                                    ]
                                                                ],
                                                                style=extend_table_style(styles["rc-main-table"], [
                                                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                                                                ]),
                                                                colWidths=(2*mm, 25*mm),
                                                                rowHeights=5*mm
                                                            ),
                                                            Paragraph("Collision", extend_style(styles["rc-normal-center"])),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                                                        ("GRID", (0, 0), (-1, -1), .75, "black"),
                                                    ]),
                                                    colWidths=(27*mm, 19*mm),
                                                    rowHeights=9*mm
                                                ),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        colWidths=(46*mm),
                                        rowHeights=(5*mm, 9*mm)
                                    ),
                                    Paragraph("Cargo<br/>Limit of<br/>Insurance", extend_style(styles["rc-normal-center"])),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(8*mm, 21*mm, 21*mm, 32*mm, 32*mm, 22*mm, 46*mm, 20*mm),
                            rowHeights=(14*mm)
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(14*mm)
            ),
        ]

        elems += [
            Table(
                [   
                    [   
                        self.physical_detail("1.")
                    ],
                    [   
                        self.physical_detail("2.")
                    ],
                    [   
                        self.physical_detail("3.")
                    ],
                    [   
                        self.physical_detail("4.")
                    ],
                    [   
                        self.physical_detail("5.")
                    ],
                    [   
                        self.physical_detail("6.")
                    ],
                    [   
                        self.physical_detail("7.")
                    ],
                    [   
                        self.physical_detail("8.")
                    ],
                    [   
                        self.physical_detail("9.")
                    ],
                    [   
                        self.physical_detail("10.")
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(4.7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("29."),
                        Paragraph("Any loss payees?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, give me name and address of mortgagee/loss of each vehicle", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2*L_S),
                ]),
                colWidths=( 6*mm, 25*mm, 25*mm, 88*mm, 58*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 7*mm, 195*mm ),
                rowHeights=5*mm
            ),
        ]

        # 2 page footer
        elems += [
            Table(
                [
                    [   
                       Paragraph("Truck Application Page 2 of 5", extend_style(styles["rc-normal-end"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                ]),
                colWidths=(202*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("LOSS EXPERIENCE", extend_style(styles["rc-normal-header"])),
                       Paragraph("- Provide prior insurance carries information for past full three years.", extend_style(styles["rc-bold-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(35*mm, 167*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("Policy Term", extend_style(styles["rc-normal-center"])),
                                ],
                                [
                                    Table(
                                        [
                                            [   
                                               Paragraph("From", extend_style(styles["rc-normal-center"])),
                                               Paragraph("To", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        rowHeights=7*mm
                                    ),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(35*mm),
                            rowHeights=(4.5*mm, 7*mm)
                        ),
                        Paragraph("Insurance Company Name", extend_style(styles["rc-normal-center"])),
                        Paragraph("No. of Motor<br/>Powered<br/>Vehicles", extend_style(styles["rc-normal-center"])),
                        Paragraph("No. of<br/>Accidents", extend_style(styles["rc-normal-center"])),
                        Table(
                            [
                                [   
                                    Paragraph("Policy Term", extend_style(styles["rc-normal-center"])),
                                ],
                                [
                                    Table(
                                        [
                                            [   
                                               Paragraph("From", extend_style(styles["rc-normal-center"])),
                                               Paragraph("To", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        rowHeights=7*mm
                                    ),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(35*mm),
                            rowHeights=(4.5*mm, 7*mm)
                        ),
                        Table(
                            [
                                [   
                                    Paragraph("Policy Term", extend_style(styles["rc-normal-center"])),
                                ],
                                [
                                    Table(
                                        [
                                            [   
                                               Paragraph("BI", extend_style(styles["rc-normal-center"])),
                                               Paragraph("PD", extend_style(styles["rc-normal-center"])),
                                               Paragraph("Comp/Coll", extend_style(styles["rc-normal-center"])),
                                               Paragraph("Other", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        rowHeights=7*mm
                                    ),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(58*mm),
                            rowHeights=(4.5*mm, 7*mm)
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(35*mm, 38*mm, 20*mm, 16*mm, 35*mm, 58*mm),
                rowHeights=11.5*mm
            ),
        ]

        elems += [
            Table(
                [   
                    [   
                        self.loss_experience()
                    ],
                    [   
                        self.loss_experience()
                    ],
                    [   
                        self.loss_experience()
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(5*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("30."),
                        Paragraph("Is any applicant aware of any facts or past incidents, circumstances or situations which could give rise to a claim under the insurance coverage", extend_style(styles["rc-first-label"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 196*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("sought in this application?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, provide complete details", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 36*mm, 25*mm, 42*mm, 93*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("31."),
                        Paragraph("Have you ever been declined, cancelled or non-renewed for this kind of insurance?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, date and why", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2*L_S),
                ]),
                colWidths=( 6*mm, 108*mm, 25*mm, 28*mm, 35*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("CARGO INFORMATION", extend_style(styles["rc-normal-header"])),
                       Paragraph("- 100% coinsurance clause applies. Use Tow Truck Suppliment for In-Tow/On Hook coverage.", extend_style(styles["rc-bold-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BACKGROUND", (0, 0), (-1, -1), "#d1d1d1"),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBELOW", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(42*mm, 160*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("PREVIOUS CARGO CARRIER AND LOSS EXPERIENCE", extend_style(styles["rc-normal-header1"])),
                       Paragraph("(list for the past three years with most recent carrier first)", extend_style(styles["rc-bold-text"])),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(85*mm, 117*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("Policy Term", extend_style(styles["rc-normal-center"])),
                                ],
                                [
                                    Table(
                                        [
                                            [   
                                               Paragraph("From", extend_style(styles["rc-normal-center"])),
                                               Paragraph("To", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                                            ("GRID", (0, 0), (-1, -1), .75, "black"),
                                        ]),
                                        rowHeights=8*mm
                                    ),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(35*mm),
                            rowHeights=(5*mm, 8*mm)
                        ),
                        Paragraph("Company & Policy Number", extend_style(styles["rc-normal-center"])),
                        Paragraph("Premium", extend_style(styles["rc-normal-center"])),
                        Paragraph("No. of<br/>Claims", extend_style(styles["rc-normal-center"])),
                        Paragraph("Clause of Loss", extend_style(styles["rc-normal-center"])),
                        Paragraph("Amount Paid", extend_style(styles["rc-normal-center"])),
                        Paragraph("Reserves", extend_style(styles["rc-normal-center"])),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(35*mm, 48*mm, 20*mm, 16*mm, 35*mm, 23*mm, 25*mm),
                rowHeights=13*mm
            ),
        ]

        elems += [
            Table(
                [   
                    [   
                        self.cargo_information()
                    ],
                    [   
                        self.cargo_information()
                    ],
                    [   
                        self.cargo_information()
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(4*mm)
            ),
        ]

        elems += self.line_spacer()

        elems += [
            Table(
                [
                    [   
                        Paragraph("Describe Cargo Hauled", extend_style(styles["rc-normal-center"])),
                        Paragraph("% of Hauling", extend_style(styles["rc-normal-center"])),
                        Paragraph("Maximum Value", extend_style(styles["rc-normal-center"])),
                        Paragraph("Average Value", extend_style(styles["rc-normal-center"])),
                        Paragraph("Limit of Insurance", extend_style(styles["rc-normal-center"])),
                        Paragraph("Deductible", extend_style(styles["rc-normal-center"])),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("GRID", (0, 0), (-1, -1), 1, "black"),
                ]),
                colWidths=(80*mm, 24*mm, 24*mm, 24*mm, 24*mm, 26*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Table(
                            [
                                [   
                                    self.describe_cargo()
                                ],
                                [   
                                    self.describe_cargo()
                                ],
                                [   
                                    self.describe_cargo()
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("GRID", (0, 0), (-1, -1), .75, "black"),
                            ]),
                            colWidths=(152*mm),
                            rowHeights=5*mm
                        ),
                        Paragraph("SEE PHYSICAL<br/>DAMAGE<br/>COVERAGE<br/>SECTION", extend_style(styles["rc-bold-center"])),
                        Table(
                            [
                                [   
                                    None,
                                    self.checkbox_text('$500', 12),
                                    None,
                                ],
                                [   
                                    None,
                                    self.checkbox_text('$1,000', 12),
                                    None,
                                ],
                                [   
                                    None,
                                    self.checkbox_text('$2,500', 12),
                                    None,
                                ],
                                [   
                                    None,
                                    self.checkbox_text('Other', 12),
                                    self.underline(),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ]),
                            colWidths=(1*mm, 12*mm, 9*mm),
                            rowHeights=3.2*mm
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(152*mm, 24*mm, 26*mm),
                rowHeights=15*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Paragraph("If applicant hauls double wide mobile homes, Limit of Insurance must be equal to the value of both sides comined to satisfy co-insurance.<br/>Amount of insurance on each truck should equal maximum load carried.", extend_style(styles["rc-normal-text"])),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), .5),
                ]),
                colWidths=(202*mm),
                rowHeights=6*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("32."),
                        Paragraph("Select type of coverage desired:", extend_style(styles["rc-first-label"])),
                        self.checkbox_text("Named Perils or", 24),
                        self.checkbox_text("Broad Form", 18),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 48*mm, 30*mm, 118*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("33."),
                        Paragraph("Additional Coverage Options (additional premium may apply):", extend_style(styles["rc-first-label"])),
                        self.checkbox_text("Additional Insured Endorsement (Lessee)", 55),
                        self.checkbox_text("Loading and Unloading Coverage", 55),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 81*mm, 59*mm, 56*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        self.checkbox_text("Earned Freight Coverage", 40),
                        self.checkbox_text("Refrigeration Breakdown Coverage", 50),
                        self.checkbox_text("Hired Car Cargo Coverage", 35),
                        self.checkbox_text("Exclude Theft Coverage", 35),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 42*mm, 51*mm, 48*mm, 51*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("FILING INFORMATION", styles["rc-divider-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-divider-table"], [
                ]),
                colWidths=(204*mm),
                rowHeights=(5*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("34."),
                        Paragraph("Is an FHWA filing required?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, MC number", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 45*mm, 25*mm, 28*mm, 98*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        self.checkbox_text("Common", 14),
                        self.checkbox_text("Contract", 12),
                        self.checkbox_text("Broker", 35),
                        Paragraph("Do you require FHWA cargo filing?", extend_style(styles["rc-first-label"])),
                        self.yes_no()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 18*mm, 18*mm, 18*mm, 49*mm, 93*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("35."),
                        Paragraph("If you hold a Brokers license, identify name filed with FHWA, FHWA docket no. and receipts from brokerage operations", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 158*mm, 38*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 8*mm, 194*mm),
                rowHeights=3.5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("36."),
                        Paragraph("If you are interstate regulated carrier, identify your registration or base state", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 98*mm, 35*mm, 63*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("37."),
                        Paragraph("Is an intrastate filing needed?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, show state and permit number", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 40*mm, 25*mm, 50*mm, 81*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("List states for which insured requires CARGO FILINGS (check name on permits)", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 108*mm, 88*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("38."),
                        Paragraph("Show exact name and address in which permits are issued", extend_style(styles["rc-first-label"])),
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 80*mm, 116*mm),
                rowHeights=4*mm
            ),
        ]   

        elems += [
            Table(
                [
                    [   
                        self.right_header("39."),
                        Paragraph("Is MCS 90 endorsement needed?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 50*mm, 146*mm),
                rowHeights=4*mm
            ),
        ]   

        elems += [
            Table(
                [
                    [   
                        self.right_header("40."),
                        Paragraph("Is our policy to cover all vehicles owned, operated or under lease to applicant?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, explain", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 102*mm, 25*mm, 20*mm, 49*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        self.underline(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2*L_S),
                ]),
                colWidths=( 8*mm, 194*mm),
                rowHeights=3.5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("41."),
                        Paragraph("Are oversize, overweight commodities hauled?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If filing required, show states", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 65*mm, 25*mm, 40*mm, 66*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("Are escort vehicles towed on return trips?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 56*mm, 140*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("42."),
                        Paragraph("Does your authority allow for transportation of hazardous commodities?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 93*mm, 103*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("43."),
                        Paragraph("Do you allow others to haul hazardous commodities under your authority?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 95*mm, 101*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("44."),
                                    Paragraph("Have you ever changed your operating name?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                    Paragraph("Do you operate under any other name?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 65*mm, 30*mm, 55*mm, 41*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("45."),
                                    Paragraph("Do you operate as a subsidiary of another company?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 73*mm, 99*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("46."),
                                    Paragraph("Do you own or manage any other transportation operations that are not covered?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 107*mm, 79*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("47."),
                                    Paragraph("Do you lease your authority?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                    Paragraph("Do you appoint agents or hire independent contractors to operate on your behalf?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 43*mm, 25*mm, 108*mm, 25*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("48."),
                                    Paragraph("Have you purchased, sold or applied for authority over the past 3 years?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 101*mm, 87*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("49."),
                                    Paragraph("Have you ever lost or had authority withdrawn, or have you been/are under probation by any regulatory authority (FHWA, PUC, etc)?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 175*mm, 23*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("50."),
                                    Paragraph("Is evidence/certificate(s) of coverage required?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 65*mm, 126*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    self.right_header("51."),
                                    Paragraph('Please explain any "yes" answer to quetions 44 through 50', extend_style(styles["rc-first-label"])),
                                    self.underline(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 79*mm, 119*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    None,
                                    self.underline(),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 8*mm, 196*mm),
                            rowHeights=3.5*mm
                        ),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2*L_S),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBELOW", (0, -1), (-1, -1), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=( 205*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("52."),
                        Paragraph("Do you have agreements with other carriers for the interchange of equipment or transportation of loads?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 135*mm, 61*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("If yes, attach a copy of current agreements and complete the following:", extend_style(styles["rc-first-label"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 8*mm, 194*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("(a)  With whome has such agreement(s) been made?", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 11*mm, 74*mm, 117*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("(b)  Do the parties names in (a) carry automobile liability insurance?", extend_style(styles["rc-first-label"])),
                        self.yes_no()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 11*mm, 89*mm, 102*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("If yes, name of insurance company and limits of liability (Bodily Injury & Property Damage)", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 15*mm, 118*mm, 69*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("(c)  Under whose permit does each of the parties to the agreement(s) operate?", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 11*mm, 104*mm, 87*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("(d)  Is there a hold harmless in the agreement(s)?", extend_style(styles["rc-first-label"])),
                        self.yes_no()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 11*mm, 67*mm, 124*mm),
                rowHeights=4*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("53."),
                        Paragraph("Do you barter, hire or lease any vehicles?", extend_style(styles["rc-first-label"])),
                        self.yes_no(),
                        Paragraph("If yes, explain", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6*mm, 57*mm, 25*mm, 20*mm, 94*mm),
                rowHeights=4*mm
            ),
        ]

        # 3 page footer
        elems += [
            Table(
                [
                    [   
                       Paragraph("Truck Application Page 3 of 5", extend_style(styles["rc-normal-end"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(202*mm),
                rowHeights=5*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("SELECTION OF LIMITS FOR UNINSURED/UNDERINSURED MOTORISTS COVERAGE<br/>(Virginia)", extend_style(styles["rc-header-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
                ]),
                colWidths=(202*mm),
                rowHeights=12*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                       Paragraph("Virginia Insurance Code Section 38.2-2206 provides that policies of insurance which provide bodily injury or property damage liability insurance relating to the ownership, maintenance or use of a motor vehicle issued or delivered in the Commonwealth of Virginia must provide Unsured motor vehicle coverage in limits not less than $25,000 because of bodily injury to or death of one person in any one accident and $50,000 because of bodily injury to or death of two or more persons in any one accident, and $20,000 because of injury to or destruction of property of others on any one accident. Such policies must also provide coverage for bodily injury or property damage caused by the operation or use of an Underinsured motor vehicle.", extend_style(styles["rc-medium-content-justify"])),
                    ],
                    [
                        None,
                    ],
                    [   
                       Paragraph("Under Virginia law, the limits of Uninsured/Underinsured motorist coverage must equal the limits of the liability insurance provided by your policy unless additional coverage is rejected by any one named insured. Therefore, if you purchase liability insurance in amounts greater than the state mandated minimum limits of $25,000/50,000/20,000, your Uninsured/Underinsured motorist coverage limits will equal these greater limits.", extend_style(styles["rc-medium-content-justify"])),
                    ],
                    [
                        None,
                    ],
                    [   
                       Paragraph("If you purchase liability limits in excess of $25,000/50,000/20,000 you may reject the increased limits of Uninsured/Underinsured motorist coverage. If you reject the increased limits of Uninsured/Underinsured motorist coverage you must at a minimum purchase the state-mandated limits of $25,000/50,000/20,000. You may also choose to purhase Uninsured/Underinsured motorist coverage limits in excess of the state-mandated minimum amount yet less than your liability insurance limits. Ask your producer for coverage limits offered.", extend_style(styles["rc-medium-content-justify"])),
                    ],
                    [
                        None,
                    ],
                    [   
                       Paragraph("The rejection of the additional limits of Uninsured/Underinsured motorist insurance by any one named insured is binding on all insureds under such policy.", extend_style(styles["rc-medium-content-justify"])),
                    ],
                    [
                        None,
                    ],
                    [   
                       Paragraph("In accordance with the Virginia law, the undersigned insured (and each of them):", extend_style(styles["rc-medium-content"])),
                    ],
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("(Applicable item marked", extend_style(styles["rc-bold-text"])),
                                    self.checkbox(True, size='small'),
                                    Paragraph(" )", extend_style(styles["rc-bold-text"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ]),
                            colWidths=(35*mm, 2.5*mm, 16*mm),
                            rowHeights=6*mm
                        )
                        
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    self.checkbox(size='small'),
                                    None,
                                    Paragraph("Selects Uninsured/Underinsured mortor vehicle coverage limits in the amount of $25,000/50,000/20,000. These are the lowest coverage limits which may be purchased by law.", extend_style(styles["rc-normal-text"])),
                                ],
                                [
                                    None,None,None,None,
                                ],
                                [   
                                    None,
                                    self.checkbox(size='small'),
                                    None,
                                    Paragraph("Selects Uninsured/Underinsured mortor vehicle coverage limits which are lower than the liability limits under the policy but higher than the state-mandated minimum limits. Selected limits for Uninsured/Underinsured motorist coverage are:", extend_style(styles["rc-normal-text"])),
                                ],
                                [
                                    None,None,None,None,
                                ],
                                [
                                    None,
                                    None,
                                    None,
                                    Paragraph("Enter limit if a separate limit of liability applies)", extend_style(styles["rc-medium-content"])),
                                ],
                                [
                                    None,
                                    None,
                                    None,
                                    Paragraph("$_______________ Bodily injury each person", extend_style(styles["rc-medium-content"])),
                                ],
                                [
                                    None,
                                    None,
                                    None,
                                    Paragraph("$_______________ Bodily injury each accident", extend_style(styles["rc-medium-content"])),
                                ],
                                [
                                    None,
                                    None,
                                    None,
                                    Paragraph("$_______________ Property Damage each accident", extend_style(styles["rc-medium-content"])),
                                ],
                                [
                                    None,
                                    None,
                                    None,
                                    None,
                                ],
                                [
                                    None,
                                    None,
                                    None,
                                    Paragraph("Enter limit if a single limit of liability applies)", extend_style(styles["rc-medium-content"])),
                                ],
                                [
                                    None,
                                    None,
                                    None,
                                    Paragraph("$_______________ Each accident", extend_style(styles["rc-medium-content"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ]),
                            colWidths=(2*mm, 3*mm, 3*mm, 192*mm),
                        )
                    ],
                    [
                        None,
                    ],
                    [   
                        Paragraph("<u>MEDIACAL EXPENSE AND INCOME LOSS BENEFITS SELECTION</u>", extend_style(styles["rc-medium-header-underline"])),
                    ],
                    [
                        None,
                    ],
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("<u>Medical Expense Benefits</u>", extend_style(styles["rc-bold-text-underline"])),
                                    Paragraph("- Choose one:", extend_style(styles["rc-medium-content"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(36*mm, 160*mm),
                        )
                    ],
                    [
                        None,
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    self.checkbox_text('Reject', 12, bold=True),
                                    None, None, None, None, None
                                ],
                                [   
                                    None,
                                    self.checkbox_text('Accept', 16, bold=True),
                                    Paragraph("If accepting, choose one:", extend_style(styles["rc-medium-content"])),
                                    self.checkbox_text('$500', 10),
                                    self.checkbox_text('$1000', 10),
                                    self.checkbox_text('$2000', 10),
                                    self.checkbox_text('$5000', 10),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(2*mm, 35*mm, 40*mm, 30*mm, 30*mm, 30*mm,30*mm),
                        ),
                    ],
                    [
                        None,
                    ],
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("<u>Income Loss Benefits</u>", extend_style(styles["rc-bold-text-underline"])),
                                    Paragraph("- Choose one:", extend_style(styles["rc-medium-content"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(31*mm, 160*mm),
                        )
                    ],
                    [
                        None,
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    self.checkbox_text('Reject', 12, bold=True)
                                ],
                                [   
                                    None,
                                    self.checkbox_text('Accept', 16, bold=True),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(2*mm, 200*mm),
                        )
                    ],
                    [
                        None,
                    ],
                    [
                        Paragraph('I have indicated my choice above ("X" indicates my choice):', extend_style(styles["rc-medium-content"])),
                    ],
                    [
                        None,
                    ],
                    [
                        None,
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    Table(
                                        [
                                            [   
                                                Paragraph("Signature of Insured", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                            ("LINEABOVE", (0, 0), (-1, -1), 0.75, 'black')
                                        ]),
                                        colWidths=(80*mm),
                                    ),
                                    None,
                                    Table(
                                        [
                                            [   
                                                Paragraph("Signature of Insured", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                            ("LINEABOVE", (0, 0), (-1, -1), 0.75, 'black')
                                        ]),
                                        colWidths=(80*mm),
                                    ),
                                    None,
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(2*mm, 80*mm, 18*mm, 80*mm, 22*mm),
                        )                        
                    ],
                    [
                        None,
                    ],
                    [
                        None,
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    Table(
                                        [
                                            [   
                                                Paragraph("Date", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                            ("LINEABOVE", (0, 0), (-1, -1), 0.75, 'black')
                                        ]),
                                        colWidths=(80*mm),
                                    ),
                                    None,
                                    Table(
                                        [
                                            [   
                                                Paragraph("Policy Number", extend_style(styles["rc-normal-center"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                            ("LINEABOVE", (0, 0), (-1, -1), 0.75, 'black')
                                        ]),
                                        colWidths=(80*mm),
                                    ),
                                    None,
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(2*mm, 80*mm, 18*mm, 80*mm, 22*mm),
                        )                        
                    ],
                    [
                        None,
                    ],
                    [
                        Paragraph("(Until you advise us otherwise in writing, your choices, as indicated above, will continue regardless of any addition or change in Auto coverage on your current policy or addition of any Scheduled Autos.)", extend_style(styles["rc-medium-content"])),
                    ],
                    [
                        None,
                    ],
                    [
                        Paragraph("SIGNATURE IS ALSO REQUIRED ON LAST PAGE OF APPLICATION", extend_style(styles["rc-medium-header-center"])),
                    ],

                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                colWidths=(202*mm),
            ),
        ]

        # 4 page footer
        elems += [
            Table(
                [
                    [   
                       Paragraph("Truck Application Page 4 of 5", extend_style(styles["rc-normal-end"])),
                    ],
                    [
                        None,
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(202*mm),
                rowHeights=7*mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Paragraph("MUST BE SIGNED BY THE APPLICANT PERSONALLY", extend_style(styles["rc-medium-header-center"])),
                    ],
                    [
                        None
                    ],
                    [
                        None
                    ],
                    [
                        Paragraph("No coverage is bound until the Company advises the <b>Applicant or its representative that a policy will be issued and then only as of the policy effective date and in accordance with all policy terms. The Apllicant acknowledges that the Applicant's Representative named below is acting as Applicant's agent and not on behalf of the Company. The Applicant's Representative has no authority to bind coverage, may not accept any funds for the Company, and may not modify or interpret the terms of the policy.</b>", extend_style(styles["rc-normal-text1"])),
                    ],
                    [
                       Paragraph("The Applicant agrees that the foregoing statements and answers are true and correct. The Applicant requests the Company to rely on its statements and answers in issuing any policy or subsequent renewal. The Applicant agrees that if its statements and answers are materially false, the Company may rescind any policy or subsequent renewal it may issue.", extend_style(styles["rc-normal-text1"])),
                    ],
                    [
                       Paragraph("If any jurisdiction in which the Applicant intends to operate or the Interstate Commerce Commision requires a special enforsement to be attached to the policy which increases the Company's liability, the Applicant agrees to reimburse the Company in accordance with the terms of that endorsement.", extend_style(styles["rc-normal-text1"]))
                    ],
                    [
                       Paragraph("The Applicant agrees that any inspection of autos, vehicles, equipment, premises, operations, or inspection of ny other matter relating to insurance that may be provided by the Company, is made for the use and benefit of the Company only, and is not to be relied upon by the Applicant or any other party in any respect.", extend_style(styles["rc-normal-text1"]))
                    ],
                    [
                       Paragraph("The Applicant understands that an inquiry may be made into the character, finances, driving records, and other personal and business background information the Company deems necessary in determining whether to bind or maintain coverage. Upon written request, additional information will be provided to the Applicant regarding any investigation.", extend_style(styles["rc-normal-text1"]))
                    ],
                    [
                       Paragraph("The Applicant represents that she/he has completed all relevant sections of this Application prior to execution and that the Applicant has personally signed below (or if Applicant is a Corporation, a corporate officer has signed below).", extend_style(styles["rc-normal-text1"]))
                    ],
                    [
                        Table(
                            [
                                [   
                                   Paragraph("Will premium financed?", extend_style(styles["rc-first-label"])),
                                   self.yes_no(),
                                   Paragraph("If yes, with whome", extend_style(styles["rc-normal-text"])),
                                   self.underline()
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ]),
                            colWidths=(45*mm, 25*mm, 30*mm, 92*mm),
                            rowHeights=5*mm
                        ),
                    ],
                    [
                        None,
                    ],
                    [
                        None,
                    ],
                    [
                        Paragraph("IT IS A CRIME TO KNOWINGLY PROVIDE FALSE, INCOMEPLETE OR MISLEADING INFORMATION TO AN INSURANCE COMPANY FOR THE PURPOSE OF DEFRAUDING THE COMPANY. PENALTIES INCLUDE IMPRISONMENT, ", extend_style(styles["rc-medium-header"])),
                    ],
                    [
                        None,
                    ],
                    [
                        None,
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(202*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("Witness", extend_style(styles["rc-normal-text"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LINEABOVE", (0, 0), (-1, -1), 0.75, 'black')
                            ]),
                            colWidths=(72*mm),
                        ),
                        None,
                        Table(
                            [
                                [   
                                    Paragraph("Applicant's Signature", extend_style(styles["rc-normal-text"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LINEABOVE", (0, 0), (-1, -1), 0.75, 'black')
                            ]),
                            colWidths=(82*mm),
                        ),
                        None,
                        Table(
                            [
                                [   
                                    Paragraph("Date", extend_style(styles["rc-normal-text"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LINEABOVE", (0, 0), (-1, -1), 0.75, 'black')
                            ]),
                            colWidths=(30*mm),
                        ),
                        None,
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                colWidths=(72*mm, 5*mm, 82*mm, 5*mm, 30*mm, 4*mm),
            )                        
        ]

        elems += [
            Table(
                [
                    [   
                       None,
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(202*mm),
                rowHeights=10*mm
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("TO BE COMPLETED BY APPLICANT'S REPRESENTATIVE", extend_style(styles["rc-bold-center"])),
                    ],
                    [
                        Table(
                            [
                                [   
                                   Paragraph("Is this direct business to your office?", extend_style(styles["rc-first-label"])),
                                   self.underline(),
                                   Paragraph("If yes, explain", extend_style(styles["rc-first-label"])),
                                   self.underline(),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ]),
                            colWidths=(49*mm, 32*mm, 21*mm, 90*mm),
                            rowHeights=5*mm
                        ),
                    ],
                    [
                        Table(
                            [
                                [   
                                   Paragraph("Is this new business to your office?", extend_style(styles["rc-first-label"])),
                                   self.underline(),
                                   Paragraph("If not, how long have you had the account?", extend_style(styles["rc-first-label"])),
                                   self.underline(),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ]),
                            colWidths=(48*mm, 28*mm, 59*mm, 57*mm),
                            rowHeights=5*mm
                        ),
                    ],
                    [
                        Table(
                            [
                                [   
                                   Paragraph("How long have you know applicant?", extend_style(styles["rc-first-label"])),
                                   self.underline(),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ]),
                            colWidths=(51*mm, 67*mm),
                            rowHeights=5*mm
                        ),
                    ],
                    [
                        Paragraph("REQUEST TO COMPANY GENERAL AGENT:", extend_style(styles["rc-medium-header"])),
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    self.checkbox_text("please quote", 20),
                                    self.checkbox_text("Please bind at earliest possible date and issue policy", 90),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ]),
                            colWidths=(2*mm, 30*mm, 100*mm),
                            rowHeights=5*mm
                        ),
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    self.checkbox_text("please issue policy effective", 38),
                                    Table(
                                        [
                                            [
                                                None,
                                            ],
                                            [   
                                                Paragraph("(Time and Date Bound by General Agent)", extend_style(styles["rc-small-underline"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                            ("LINEABOVE", (0, -1), (-1, -1), 0.75, 'black')
                                        ]),
                                        colWidths=(42*mm),
                                        rowHeights=(5*mm, 3*mm)
                                    ),
                                    Paragraph("Coverage was bound by", extend_style(styles["rc-medium-header"])),
                                    Table(
                                        [
                                            [
                                                None,
                                            ],
                                            [   
                                                Paragraph("(Name of Person in Company General Agency's Office Binding Coverage)", extend_style(styles["rc-small-underline"])),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                            ("LINEABOVE", (0, -1), (-1, -1), 0.75, 'black')
                                        ]),
                                        colWidths=(71*mm),
                                        rowHeights=(5*mm, 3*mm)
                                    ),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ]),
                            colWidths=(2*mm, 40*mm, 44*mm, 35*mm, 72*mm),
                            rowHeights=8*mm
                        ),
                    ],
                    [
                        None,
                    ],
                    [
                        None,
                    ],
                    [
                        Table(
                            [
                                [   
                                    None,
                                    Paragraph("Applicant's Representative's Name and Address", extend_style(styles["rc-normal-center"])),
                                    Paragraph("Phone No.", extend_style(styles["rc-normal-center"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LINEABOVE", (1, 0), (-1, -1), 0.75, 'black')
                            ]),
                            colWidths=(2*mm, 100*mm, 90*mm),
                        ),
                    ],
                    [
                        None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2*L_S),
                    ("LINEABOVE", (0, 0), (-1, 0), .75, "black"),
                    ("LINEBELOW", (0, -1), (-1, -1), .75, "black"),
                    ("LINEBEFORE", (0, 0), (0, -1), .75, "black"),
                    ("LINEAFTER", (-1, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=( 202*mm),
                rowHeights=5*mm
            ),
        ]

        # footer page 5
        elems += [
            Table(
                [
                    [   
                       Paragraph("Truck Application Page 5 of 5", extend_style(styles["rc-normal-end"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(202*mm),
                rowHeights=69*mm
            ),
        ]

        return elems
