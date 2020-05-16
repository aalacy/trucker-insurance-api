# -*- coding: utf-8 -*-
import cStringIO
from datetime import datetime as date
import json

from document_specific_styles import *
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Flowable, Paragraph, Table, Spacer


def coi(title='COI.pdf', author="Luckytruck", name="", address="", policy="{}"):
    cr =ROCReport(title, author, name, address, policy)
    buff = cStringIO.StringIO()
    return cr.create_report(buff)

class ROCReport:
    BASE_PATH = os.path.abspath(os.curdir) + '/routes/coi'

    def __init__(self, title=None, author="Luckytruck", name="", address="", policy=None):
        self.page_size = letter
        self.page_margin = (7.9 * mm, 6.4 * mm)
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
                        Paragraph(
                            "<img src='{}/img/accord.png' width='80' height='30' />".format(self.BASE_PATH),                
                            extend_style(styles["rc-main-rmt"])
                        ),
                        Paragraph(
                            "CERTIFICATE OF LIABILITY INSURANCE",                
                            extend_style(styles["rc-my-doc-header"])
                        ),
                        Table(
                            [
                                [
                                    Paragraph(
                                        "DATE (MM/DD/YYYY)",                
                                        extend_style(styles["rc-small-header-center"])
                                    )
                                ],
                                [
                                    Paragraph(
                                        date.now().strftime("%m/%d/%Y"),                
                                        extend_style(styles["rc-medium-content"])
                                    )
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                    ("OUTLINE", (0, 0), (-1, -1), 1, "black"),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ]),
                            colWidths=(35 * mm),
                        )
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                                    ]),
                colWidths=(35 * mm, 132 * mm, 35 * mm),
                rowHeights=8.4 * mm
            ),
        ]
            
        return elems

    def checkbox(self, checked=None):
        x = ''
        if checked:
            x = 'X'
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
            colWidths=(5.8*mm),
            rowHeights=(5.2*mm)
        )

    def insurer(self, title, val, naic):
        return  Table(
                    [
                        [
                            Table(
                                [
                                    [
                                        Paragraph("{}".format(title), styles["rc-small-header"]),
                                        Paragraph("{}".format(val), styles["rc-tdwp-main-chk"]),
                                    ],
                                ],
                                style=extend_table_style(styles["rc-main-table"], [
                                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                ]),
                                colWidths=(16 * mm, 64 * mm),
                            ),
                            Paragraph("{}".format(naic), styles["rc-tdwp-main-chk"]),
                        ]
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                        ("LINEAFTER", (0, 0), (0, -1), 1, "black"),
                        ("LINEBELOW", (0, 0), (1, -1), 1, "black"),
                    ]),
                    colWidths=(80 * mm, 21 * mm),
                    rowHeights=(4 * mm),
                )

    def _section_content(self):        
        elems = [
            Table(
                [
                    [
                        Paragraph("<b>THIS CERTIFICATE IS ISSUED AS A MATTER OF INFORMATION ONLY AND CONFERS NO RIGHTS UPON THE CERTIFICATE HOLDER. THIS CERTIFICATE DOES NOT AFFIRMATIVELY OR NEGATIVELY AMEND, EXTEND OR ALTER THE COVERAGE AFFORDED BY THE POLICIES BELOW. THIS CERTIFICATE OF INSURANCE DOES NOT CONSTITUTE A CONTRACT BETWEEN THE ISSUING INSURER(S), AUTHORIZED REPRESENTATIVE OR PRODUCER, AND THE CERTIFICATE HOLDER.</b>", styles["rc-table-first"]),
                    ],
                    [
                        Paragraph("<b>IMPORTANT: If the certificate holder is an ADDITIONAL INSURED, the policy(ies) must be endorsed. If SUBROGATION IS WAIVED, subject to the terms and conditions of the policy, certain policies may require an endorsement. A statement on this certificate does not confer rights to the certificate holder in lieu of such endorsement(s).</b>", styles["rc-table-first"]),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("GRID", (0, 0), (-1, -1), 1, "black"),
                ]),
                colWidths=(202 * mm),
                rowHeights=(14.6 * mm, 10.6 * mm)
            ),
            Table(
                [
                    [   
                        Table(
                            [
                                [
                                    Paragraph("PRODUCER", styles["rc-small-header"]),
                                ],
                                [
                                    Paragraph("LuckyTruck, Inc. <br /> 555 Stanley Ave <br /> Cincinnati, Ohio 45226", styles["rc-big-para"]),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(101 * mm),
                            rowHeights=(2.4 * mm, 16.4 * mm)
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
                                                            Paragraph("CONTACT", styles["rc-small-header"]),
                                                        ],
                                                        [
                                                            Paragraph("NAME:", styles["rc-small-header"]),
                                                        ],
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                ),
                                                Paragraph(self.name, styles["rc-tdwp-main-chk"]),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        ]),
                                        colWidths=(13 * mm, 88 * mm)
                                    ),
                                ],
                                [
                                    Table(
                                        [
                                            [
                                                Table(
                                                    [
                                                        [
                                                            Table(
                                                                [
                                                                    [
                                                                        Table(
                                                                            [
                                                                                [
                                                                                    Paragraph("PHONE", styles["rc-small-header"]),
                                                                                ],
                                                                                [
                                                                                    Paragraph("(A/C, No, Ext):", styles["rc-small-header"]),
                                                                                ],
                                                                            ],
                                                                            style=extend_table_style(styles["rc-main-table"], [
                                                                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                                            ]),
                                                                        ),
                                                                        Paragraph("", styles["rc-tdwp-main-chk"]),
                                                                    ]
                                                                ],
                                                                style=extend_table_style(styles["rc-main-table"], [
                                                                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                                ]),
                                                                colWidths=(16 * mm, 34 * mm)
                                                            ),
                                                        ],
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                    ]),
                                                    rowHeights=5 * mm
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
                                                                                    Paragraph("FAX", styles["rc-small-header"]),
                                                                                ],
                                                                                [
                                                                                    Paragraph("(A/C, No):", styles["rc-small-header"]),
                                                                                ],
                                                                            ],
                                                                            style=extend_table_style(styles["rc-main-table"], [
                                                                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                                            ]),
                                                                        ),
                                                                        Paragraph("", styles["rc-tdwp-main-chk"]),
                                                                    ]
                                                                ],
                                                                style=extend_table_style(styles["rc-main-table"], [
                                                                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                                ]),
                                                                colWidths=(13 * mm, 37 * mm)
                                                            ),
                                                        ],
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                    ("LINEAFTER", (0, 0), (0, -1), 1, "black"),
                                                    ]),
                                                    rowHeights=5 * mm
                                                )
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        ]),
                                        rowHeights=5 * mm
                                    )
                                ],
                                [
                                    Table(
                                        [
                                            [
                                                Table(
                                                    [
                                                        [
                                                            Paragraph("Email", styles["rc-small-header"]),
                                                        ],
                                                        [
                                                            Paragraph("ADDRESS:", styles["rc-small-header"]),
                                                        ],
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                    ]),
                                                ),
                                                Paragraph("", styles["rc-tdwp-main-chk"]),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        ]),
                                        colWidths=(13 * mm, 88 * mm)
                                    ),
                                ],
                                [
                                    Table(
                                        [
                                            [
                                                Paragraph("INSURER(S) AFFORDING COVERAGE", styles["rc-small-header-center"]),
                                                Paragraph("NAIC #", styles["rc-small-header-center"]),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                            ("LINEAFTER", (0, 0), (0, -1), 1, "black"),
                                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                        ]),
                                        colWidths=(80 * mm, 21 * mm),
                                        rowHeights=(5 * mm)
                                    ),
                                ],
                                [
                                    self.insurer("INSURER A : ", "Progressive Mountain Insurance Company", "")
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                ("LINEBELOW", (0, 0), (-1, -1), 1, "black"),
                            ]),
                            rowHeights=(5 * mm),
                        ),
                    ],
                    [
                        Table(
                            [
                                [
                                    Paragraph("INSURED", styles["rc-small-header"]),
                                ],
                                [
                                    Paragraph("CDN Logistics, Inc. <br /> 460 CARRIAGE GATE TRL SW <br /> ATLANTA, GA 30331-6842 USA <br /> (973) 902-3177", styles["rc-big-para1"]),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            colWidths=(101 * mm),
                            # rowHeights=(2.4 * mm, 18.4 * mm)
                        ),
                        Table(
                            [
                                [
                                    self.insurer("INSURER B : ", "", "")
                                ],
                                [
                                    self.insurer("INSURER C : ", "", "")
                                ],
                                [
                                    self.insurer("INSURER D : ", "", "")
                                ],
                                [
                                    self.insurer("INSURER E : ", "", "")
                                ],
                                [
                                    self.insurer("INSURER F : ", "", "")
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                        )
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("GRID", (0, 0), (-1, -1), 1, "black"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                colWidths=(101 * mm, 101 * mm),
                # rowHeights=(22.4 * mm, 23.2 * mm)
            ),
            
            # new row
            Table(
                [
                    [
                        Paragraph("COVERAGE", styles["rc-medium-header"]),
                        Paragraph("CERTFICATE NUMBER: ", styles["rc-medium-header"]),
                        Paragraph("REVISION NUMBER", styles["rc-medium-header-center"]),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                colWidths=(40 * mm, 61 * mm, 101 * mm),
                rowHeights=(3.8 * mm)
            ),

            # new table for new row
            Table(
                [
                    [
                        Paragraph("THIS IS TO CERTIFY THAT THE POLICIES OF INSURANCE LISTED BELOW HAVE BEEN ISSUED TO THE INSURED NAMED ABOVE FOR THE POLICY PERIOD INDICATED. NOTWITHSTANDING ANY REQUIREMENT, TERM OR CONDITION OF ANY CONTRACT OR OTHER DOCUMENT WITH RESPECT TO WHICH THIS CERTIFICATE MAY BE ISSUED OR MAY PERTAIN, THE INSURANCE AFFORDED BY THE POLICIES DESCRIBED HEREIN IS SUBJECT TO ALL THE TERMS, EXCLUSIONS AND CONDITIONS OF SUCH POLICIES. LIMITS SHOWN MAY HAVE BEEN REDUCED BY PAID CLAIMS.", styles["rc-table-first"]),
                    ],
                    [
                        Table(
                            [
                                [
                                    Paragraph("INSR LTR", styles["rc-small-header-center"]),
                                    Paragraph("TYPE OF INSURANCE", styles["rc-small-header-center"]),
                                    Paragraph("ADDL INSR", styles["rc-small-header-center"]),
                                    Paragraph("SUBR WVD", styles["rc-small-header-center"]),
                                    Paragraph("POLICY NUMBER", styles["rc-small-header-center"]),
                                    Paragraph("POLICY EFF (MM/DD/YYYY)", styles["rc-small-header-center"]),
                                    Paragraph("POLICY EXP (MM/DD/YYYY)", styles["rc-small-header-center"]),
                                    Paragraph("LIMITS", styles["rc-small-header-center"]),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("GRID", (0, 0), (-1, -1), .45, "black"),
                            ]),
                            colWidths=(7*mm, 48*mm, 8*mm, 7*mm, 42*mm, 18*mm, 18*mm, 54*mm),
                            rowHeights=(5.2 * mm)
                        )
                    ],
                    [
                        Table(
                            [
                                [
                                    None,
                                    Table(
                                        [
                                            [
                                                Paragraph("<b>GENERAL LIABILITY</b>", styles["rc-small-content"]),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            Paragraph("COMMERCIAL GENERAL LIABILITY", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(5.8*mm, 32.2*mm),
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            self.checkbox(),
                                                            Paragraph("CLAIMS-MADE", styles["rc-small-content"]),
                                                            self.checkbox(),
                                                            Paragraph("OCCUR", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(5.8*mm, 5.8*mm, 15.6*mm, 5.8*mm, 15*mm),
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            None,
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
                                                    ]),
                                                    colWidths=(5.8*mm, 2*mm, 38.2*mm),
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            None,
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
                                                    ]),
                                                    colWidths=(5.8*mm, 2*mm, 38.2*mm),
                                                ),
                                            ],
                                            [
                                                Paragraph("GEN'L AGGREGATE LIMIT APPLIES PER:", styles["rc-small-content"]),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            Paragraph("POLICY", styles["rc-small-content"]),
                                                            self.checkbox(),
                                                            Paragraph("PROJECT", styles["rc-small-content"]),
                                                            self.checkbox(),
                                                            Paragraph("LOC", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(5.8*mm, 9.9*mm, 5.8*mm, 10*mm, 5.8*mm, 9.6*mm),
                                                ),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                        ]),
                                        rowHeights=(5.2*mm)
                                    ),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Table(
                                        [
                                            [
                                                Paragraph("EACH OCCURRENCE", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("DAMAGE TO RENTED <br /> PREMISES (Ea occurrence)", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("EACH OCCURRENCE", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("MED EXP (Any one person)", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("PERSONAL & ADV INJURY", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("GENERAL AGGREGATE", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("PRODUCTS - COMP/OP AGG", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                            ("GRID", (0, 0), (-1, -1), .45, "black"),
                                        ]),
                                        colWidths=(31*mm, 23*mm),
                                        rowHeights=(4.55* mm)
                                    ),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                ("GRID", (0, 0), (-1, -1), .45, "black"),
                            ]),
                            colWidths=(7*mm, 48*mm, 8*mm, 7*mm, 42*mm, 18*mm, 18*mm, 54*mm),
                            # rowHeights=(5.2 * mm)
                        )
                    ],
                    [
                        Table(
                            [
                                [
                                    None,
                                    Table(
                                        [
                                            [
                                                Paragraph("<b>AUTOMOBILE LIABILITY</b>", styles["rc-small-content"]),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            Paragraph("ANY AUTO", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(5.8*mm, 32.2*mm),
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            Paragraph("ALL OWNED<br/>AUTOS", styles["rc-small-content"]),
                                                            self.checkbox(),
                                                            Paragraph("SCHEDULED<br /> AUTOS", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(5.8*mm, 17.1*mm, 5.8*mm, 17.1*mm),
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            Paragraph("HIRED AUTOS", styles["rc-small-content"]),
                                                            self.checkbox(),
                                                            Paragraph("NON-OWNED<br /> AUTOS", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(5.8*mm, 17.1*mm, 5.8*mm, 17.1*mm),
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            self.checkbox(),
                                                            Paragraph(" ", styles["rc-small-content"]),
                                                            self.checkbox(),
                                                            Paragraph(" ", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(5.8*mm, 17.1*mm, 5.8*mm, 17.1*mm),
                                                ),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                        ]),
                                        rowHeights=(5.2*mm)
                                    ),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph(self.validate(self.policy.get('policyId', '')), styles["rc-small-header-center"]),
                                    Paragraph(self.validate(self.policy.get('effectiveDate', '')), styles["rc-small-header-center"]),
                                    Paragraph(self.validate(self.policy.get('expiryDate', '')), styles["rc-small-header-center"]),
                                    Table(
                                        [
                                            [
                                                Paragraph("COMBINED SINGLE LIMIT <br /> <small>(Ea accident)</small>", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("BODILY INJURY <small>(Per person)</small>", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("BODILY INJURY <small>(Per accident)</small>", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("COMBINED SINGLE LIMIT <br /> <small>(Per accident)</small>", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                            ("GRID", (0, 0), (-1, -1), .45, "black"),
                                        ]),
                                        colWidths=(31*mm, 23*mm),
                                        rowHeights=(5.2 * mm)
                                    ),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                ("GRID", (0, 0), (-1, -1), .45, "black"),
                            ]),
                            colWidths=(7*mm, 48*mm, 8*mm, 7*mm, 42*mm, 18*mm, 18*mm, 54*mm),
                            # rowHeights=(5.2 * mm)
                        )
                    ],
                    [
                        Table(
                            [
                                [
                                    None,
                                    Table(
                                        [
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            Paragraph("WORKERS COMPENSATION <br /> AND EMPLOYERS' LIABILITY", styles["rc-small-header"]),
                                                            Paragraph("Y/N", styles["rc-small-header-center"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(39.2*mm, 7.8*mm),
                                                ),
                                            ],
                                            [
                                                Table(
                                                    [
                                                        [   
                                                            Paragraph("ANY PROPRIETOR/PARTNER/EXECUTIVE OFFICER/MEMBER EXCLUDED?", styles["rc-small-content"]),
                                                            None,
                                                            self.checkbox(),
                                                            None,
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                                    ]),
                                                    colWidths=(38.2*mm, 2*mm, 5.8*mm, 1*mm),
                                                ),
                                            ],
                                            [
                                                Paragraph("(Mandatory in NH)", styles["rc-small-header"])
                                            ],
                                            [
                                                Paragraph("<small>If yes, describe under</small> <br /> DESCRIPTION OF OPERATIONS <small>below</small>", styles["rc-small-content"])
                                            ],

                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                        ]),
                                    ),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Table(
                                        [
                                            [
                                                Table(
                                                    [
                                                        [
                                                            Paragraph("", styles["rc-small-content"]),
                                                            Paragraph("WC STATU TORY LIMITS", styles["rc-small-content"]),
                                                            Paragraph("", styles["rc-small-content"]),
                                                            Paragraph("OTHER", styles["rc-small-content"]),
                                                        ]
                                                    ],
                                                    style=extend_table_style(styles["rc-main-table"], [
                                                        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                                        ("LINEAFTER", (0, 0), (0, -1), .45, "black"),
                                                        ("LINEAFTER", (0, 0), (1, -1), .45, "black"),
                                                        ("LINEAFTER", (0, 0), (2, -1), .45, "black"),
                                                         ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                                                    ]),
                                                    colWidths=(5*mm, 14*mm, 5*mm, 7*mm),
                                                    rowHeights=(5.4*mm)
                                                ),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("E.L. EACH ACCIDENT", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("E.L. DISEASE - EA EMPLOYEE", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                            [
                                                Paragraph("E.L. DISEASE - POLICY LIMIT", styles["rc-small-content"]),
                                                Paragraph("$", styles["rc-tdwp-main-chk"]),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                            ("GRID", (0, 0), (-1, -1), .45, "black"),
                                        ]),
                                        colWidths=(31*mm, 23*mm),
                                        rowHeights=(5.2 * mm)
                                    ),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("GRID", (0, 0), (-1, -1), .45, "black"),
                            ]),
                            colWidths=(7*mm, 48*mm, 8*mm, 7*mm, 42*mm, 18*mm, 18*mm, 54*mm),
                            # rowHeights=(5.2 * mm)
                        )
                    ],
                    [
                        Table(
                            [
                                [
                                    None,
                                    Table(
                                        [
                                            [
                                                Paragraph("2018 Freightliner X125645T", styles["rc-medium-content-center"]),
                                            ],
                                            [
                                                Paragraph("Deductible", styles["rc-medium-content-center"]),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                        ]),
                                    ),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Paragraph("", styles["rc-small-header-center"]),
                                    Table(
                                        [
                                            [
                                                Paragraph("$120,000 Stated Value", styles["rc-medium-content-center"]),
                                            ],
                                            [
                                                Paragraph("$2,500", styles["rc-medium-content-center"]),
                                            ],
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                        ]),
                                        rowHeights=(5.6 * mm)
                                    ),
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("GRID", (0, 0), (-1, -1), .45, "black"),
                            ]),
                            colWidths=(7*mm, 48*mm, 8*mm, 7*mm, 42*mm, 18*mm, 18*mm, 54*mm),
                            # rowHeights=(5.2 * mm)
                        )
                    ],
                    [
                        Table(
                            [
                                [
                                    Paragraph("DESCRIPTION OF OPERATIONS / LOCATIONS / VEHICLES (Attach ACORD 101, Additional Remarks Schedule, if more space is required)", styles["rc-small-header"]),
                                ],
                                [
                                    Paragraph("Penske Truck Leasing CO, LP and its partners are named as additional insured and loss payee for all vehicles leased or rented from Penske Truck Leasing CO, LP, including substituted, extra permanent, replacement, or in interim vehicles. Please be advised that additional insureds and loss payees will be notified in the event of mid-term cancellation.", styles["rc-big-para"]),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]),
                            rowHeights=(2.2*mm, 13*mm)
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 1, "black"),
                ]),
                # rowHeights=(3.8 * mm)
                colWidths=(202*mm)
            ),

            Table(
                [
                    [
                        Paragraph("CERTIFICATE HOLDER", styles["rc-medium-header"]),
                        Paragraph("CANCELLATION", styles["rc-medium-header"]),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                colWidths=(101*mm, 101*mm)
            ),

            Spacer(0, 4.2 * mm),
            
            Table(
                [
                    [
                        Paragraph("{} <br /> {}".format(self.name, self.address), styles["rc-big-para"]),
                        Table(
                            [
                                [
                                    Table(
                                        [
                                            [
                                                Paragraph("SHOULD ANY OF THE ABOVE DESCRIBED POLICIES BE CANCELLED BEFORE THE EXPIRATION DATE THEREOF, NOTICE WILL BE DELIVERED IN ACCORDANCE WITH THE POLICY PROVISIONS.", styles["rc-small-header"]),
                                            ]
                                        ],
                                         style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                                            ("TOPPADDING", (0, 0), (-1, -1), 2),
                                        ]),
                                    )
                                ],
                                [
                                    Table(
                                        [
                                            [
                                                Paragraph("AUTHORIZED REPRESENTATIVE", styles["rc-small-header"]),
                                            ],
                                            [
                                                Paragraph('<img src="{}/img/signature.png" width="90" height="30" />'.format(self.BASE_PATH), 
                                                    extend_style(styles["rc-main-rmt"])
                                                ),
                                            ]
                                        ],
                                        style=extend_table_style(styles["rc-main-table"], [
                                            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                        ]),
                                        rowHeights=(2.5*mm, 12*mm)
                                    )
                                ]
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("GRID", (0, 0), (-1, -1), 1, "black"),
                            ]),
                        )
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 1, "black"),
                ]),
                colWidths=(101*mm, 101*mm)
            ),

            Table(
                [
                    [
                        Paragraph("ACORD 25 (2010/05)", styles["rc-medium-header"]),
                        Paragraph("© 1988-2010 ACORD CORPORATION. All rights reserved.", styles["rc-medium-header-right"]),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 1, "black"),
                ]),
                colWidths=(101*mm, 101*mm)
            ),

            Spacer(0, 2.2 * mm),

            Paragraph("The ACORD name and logo are registered marks of ACORD", styles["rc-medium-header-center"]),
        ]       
        return elems

class CheckBox(Flowable):
    def __init__(self, checked=None):
        Flowable.__init__(self)
        self.checked = checked
        self.draw()

    def draw(self):
        x = ''
        if self.checked:
            x = 'X'
        Table(
            [
                [   
                    Paragraph("{}".format(x), styles["rc-small-content"]),
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 1, "black"),
            ]),
            colWidths=(5*mm),
        )

class XBox(Flowable):
    def __init__(self, size, checked=None):
        Flowable.__init__(self)
        self.width = size
        self.height = size
        self.size = size
        self.checked = checked

    def draw(self):
        self.canv.saveState()
        self.canv.setLineWidth(0.05 * self.size)
        self.canv.rect(0, 0, self.width, self.height)
        if self.checked is True:
            self.check()
        self.canv.restoreState()

    def check(self):
        self.canv.setFont('Times-Bold', self.size * 0.95)
        to = self.canv.beginText(self.width * 0.13, self.height * 0.155)
        to.textLine("X")
        self.canv.drawText(to)