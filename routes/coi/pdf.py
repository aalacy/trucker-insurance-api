# -*- coding: utf-8 -*-
import cStringIO
from datetime import datetime as date
import json

from document_specific_styles import *
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Flowable, Paragraph, Table, Spacer, PageBreak

L_S = 2.2 

def pdf(title='application.pdf', author="Luckytruck", company={}):
    cr =ROCReport(title=title, company=company)
    buff = cStringIO.StringIO()
    return cr.create_report(buff)

class ROCReport:
    BASE_PATH = os.path.abspath(os.curdir) + '/routes/pdf'

    def __init__(self, title=None, author="Luckytruck", company=None):
        self.page_size = letter
        self.page_margin = (7 * mm, 6.4 * mm)
        self.sections = ["header", "content"]
        self.title = title
        self.author = author
        self.company = company
        self.name = company['name']
        self.dba = company['dba']
        self.mc_number = company['mcNumber']
        self.email_address = company['emailAddress']
        self.phone_number = company['phoneNumber']
        self.dot_number = company['dotNumber']
        self.mailing_address = json.loads(company['mailingAddress'])
        self.garaging_addr = json.loads(company['garagingAddress'])
        self.business_structure = company['businessStructure']
        self.drivers_information_list =json.loads( company['driverInformationList'])
        self.vehicles_trailers_list = json.loads(company['vehicleInformationList'])['vehicle'] + json.loads(company['vehicleInformationList'])['trailer']
        self.cargo_hauled_list = json.loads(company['cargoHauled'])
        self.owners_list = json.loads(company['ownerInformationList'])
        self.signature = json.loads(company['signSignature'])['imageSign']   

    def validate(self, val):
        if val:
            return val.strip()
        else:
            return ""

    def create_report(self, buff=None):
    	def page_number(canv, doc):
            page_num = Table(
                [
                    [   
                        Paragraph("LuckyTruck", extend_style(styles["rc-medium-content-right"])),
                        Paragraph(str(doc.page), extend_style(styles["rc-medium-content-right"]))
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),

                ]),
                colWidths=(205*mm, 10*mm ),
            )
            page_num.wrapOn(canv, self.page_size[0], 0)
            page_num.drawOn(canv, 0, 3.8*mm)

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
        ], onPage=page_number)
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
    
    def underline(self, text="&nbsp;"):
        return  Table(
                    [
                        [ 
                            Paragraph(text, styles["rc-normal-text"]),
                        ]
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                        ("LINEBELOW", (0, 0), (-1, -1), .45, "black"),
                    ]),
                )

    def checkbox(self, checked=None, size='medium'):
        x = ''
        if checked:
            x = 'x'
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

    def dot_text(self, text):
    	return [
            Table(
                [
                    [	
	                    None,
                    	Paragraph(
                            "&bull;",                
                            extend_style(styles["rc-medium-content"])
                        ),
                        Paragraph(
                            text,                
                            extend_style(styles["rc-medium-content"])
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]),
                colWidths=(5*mm, 5*mm, 80*mm),
                rowHeights=(6*mm)
            ),
        ]

    def driver_information(self):
        drivers = []
        for number in range(0, 5):
            if number >= len(self.drivers_information_list):
                driver = {
                    'firstName': '&nbsp;',
                    'lastName': '',
                    'dobY': '',
                    'dobM': '',
                    'dobD': '',
                    'dohY': '',
                    'dohM': '',
                    'dohD': '',
                    'state': '',
                    'licenseNumber': '',
                    'CDL': ''
                }
            else:
                driver = self.drivers_information_list[number]

            dob = '{}-{}-{}'.format(driver['dobM'], driver['dobD'], driver['dobY'])
            doh = '{}-{}-{}'.format(driver['dohM'], driver['dohD'], driver['dohY'])
            if number >= len(self.drivers_information_list):
                dob = ''
                doh = ''
            drivers.append(
                Table(
                    [
                        [   
                           Paragraph(driver['firstName'] + ' ' + driver['lastName'], extend_style(styles["rc-normal-text"])),
                           Paragraph(dob, extend_style(styles["rc-normal-text"])),
                           Paragraph(str(driver['state']), extend_style(styles["rc-normal-text"])),
                           Paragraph(str(driver['licenseNumber']), extend_style(styles["rc-normal-text"])),
                           Paragraph(doh, extend_style(styles["rc-normal-text"])),
                           Paragraph(str(driver['CDL']), extend_style(styles["rc-normal-text"])),
                           Paragraph("", extend_style(styles["rc-normal-text"])),
                        ]
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), .15, "black"),
                    ]),
                    colWidths=(40*mm, 20*mm, 15*mm, 40*mm, 20*mm, 24*mm, 45*mm),
                ),
            )

        return drivers

    def vehicle_trailer(self):
        vehicles = []
        for number in range(0, 5):
            if number >= len(self.vehicles_trailers_list):
                vehicle = {
                    'year': '&nbsp;',
                    'make': '',
                    'vehicleType': '',
                    'VIN': '',
                    'zipCode': '',
                    'radiusOfTravelVehicle': '',
                }
            else:
                vehicle = self.vehicles_trailers_list[number]

            vehicles.append(Table(
                [
                    [   
                       Paragraph(str(vehicle['VIN']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['year']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['make']), extend_style(styles["rc-normal-text"])),
                       Paragraph(vehicle.get('vehicleType', ''), extend_style(styles["rc-normal-text"])),
                       Paragraph(vehicle.get('zipCode', ''), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle.get('radiusOfTravelVehicle', '')), extend_style(styles["rc-normal-text"])),
                       None,
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .45, "black"),
                ]),
                colWidths=(44*mm, 12*mm, 25*mm, 30*mm, 25*mm, 53*mm, 15*mm),
            ))
        return vehicles

    def cargo_hauled(self):
    	res = []
    	hauled = []
        for key, value in self.cargo_hauled_list.items():
        	hauled.append(key + ': ' + ','.join(value))
        if len(hauled) < 3:
        	hauled += ['&nbsp;'] * (3-len(hauled))
        for value in hauled:
            res.append(Table(
                [
                    [   
                       Paragraph(value, extend_style(styles["rc-normal-text"])),
                       Paragraph('', extend_style(styles["rc-normal-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .45, "black"),
                ]),
                colWidths=(110*mm, 94*mm),
            ))
        return res

    def owners_block(self):
        owners = []
        for number in range(0, max(3, len(self.owners_list))):
            if number >= len(self.owners_list):
                owner = {
                    'first_name': '&nbsp;',
                    'dob': '&nbsp;',
                    'mailing_address': '&nbsp;',
                }
            else:
            	_owner = self.owners_list[number]
                owner = {
            	 	'first_name': _owner['firstName'],
                    'dob': '{}-{}-{}'.format(_owner['dobM'], _owner['dobD'], _owner['dobY']),
                    'mailing_address': '{} {}, {} {}'.format(_owner['address'], _owner['city'], _owner['state'], _owner['zip']),
                }

            owners.append(Table(
                [
                    [   
                       Paragraph(str(owner['first_name']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(owner['dob']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(owner['mailing_address']), extend_style(styles["rc-normal-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .45, "black"),
                ]),
                colWidths=(65*mm, 45*mm, 94*mm),
            ))
        return owners

    def _section_header(self):        
        elems = list()
        elems += [
            Table(
                [
                    [
                        Paragraph(
                            "Truck Insurance Application",                
                            extend_style(styles["rc-pdf-header"])
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                rowHeights=12.4 * mm
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("Policy Term From:", extend_style(styles["rc-first-label"])),
                        self.underline(),
                        Paragraph("To:", extend_style(styles["rc-first-label"])),
                        self.underline()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]),
                colWidths=( 121 * mm, 25 * mm, 25 * mm, 6*mm, 25*mm),
            ),
        ]

        elems += [Spacer(width=0, height=5)]

        return elems

    def _section_content(self):     
        name_dba = self.name
        if self.dba:
            name_dba += '({})'.format(self.dba)   

        elems = [
            Table(
                [
                    [ 
                        Paragraph("Providing Any of The Following Documents Will Enable Us To Get You The Cheapest Quotes In The Least Amount of Time!", styles["rc-white-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-pdfdivider-table"], [
                ]),
                rowHeights=(8*mm),
                colWidths=(204*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.dot_text("Any Previously Completed Applications"),
                        self.dot_text("Insurance Requirements Documentation")
                    ],
                    [   
                        self.dot_text("Picture of Driver(s) License and Registration(s)"),
                        self.dot_text("Schedule of vehicles and drivers")
                    ],
                    [   
                        self.dot_text("MVR Report"),
                        self.dot_text("IFTA - all 4 quarters")
                    ],
                    [   
                        self.dot_text("Loss Runs (3-5 years as applicable)"),
                        self.dot_text("A copy of rental/lease agreement for leased vehicles")
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
            ),
        ]  

        elems += self.line_spacer()

        elems += [
            Table(
                [
                    [ 
                        Paragraph("General Information", styles["rc-white-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-pdfdivider-table"], [
                ]),
                rowHeights=(7*mm),
                colWidths=(204*mm)
            ),
        ]

        name_dba = self.name
        if self.dba:
            name_dba += '({})'.format(self.dba)   

        elems += [
            Table(
                [
                    [ 
                        Paragraph('Company Name (and "dba")', styles["rc-main-content"]),
                        self.underline(name_dba),
                        None,
                        Paragraph('Phone Number', styles["rc-main-content"]),
                        self.underline(self.phone_number),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(42*mm, 70*mm, 5*mm, 23*mm, 30*mm, 30*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                     	Paragraph("Mailing Address:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['address']),
                        Paragraph("City:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['city']),
                        Paragraph("State:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['state']),
                        Paragraph("Zip:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['zip']),
                        None
                    ],
                    [ 
                     	Paragraph("Garaging Address:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['address']),
                        Paragraph("City:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['city']),
                        Paragraph("State:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['state']),
                        Paragraph("Zip:", extend_style(styles["rc-main-content"])),
                        self.underline(self.mailing_address['zip']),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(28*mm, 70*mm, 8*mm, 30*mm, 10*mm, 16*mm, 8*mm, 20*mm, 10*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('E-mail Address:', styles["rc-main-content"]),
                        self.underline(self.email_address),
                        None,
                        Paragraph('Business start date:', styles["rc-main-content"]),
                        self.underline(),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(25*mm, 50*mm, 5*mm, 30*mm, 30*mm, 60*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('DOT Number:', styles["rc-main-content"]),
                        self.underline(self.dot_number),
                        None,
                        Paragraph('MC Number:', styles["rc-main-content"]),
                        self.underline(),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(22*mm, 40*mm, 5*mm, 20*mm, 30*mm, 83*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('Radius of travel:', styles["rc-main-content"]),
                        self.underline(self.dot_number),
                        Paragraph('Current Carrier:', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('Current ELD Provider:', styles["rc-main-content"]),
                        self.underline(),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(26*mm, 30*mm, 25*mm, 40*mm, 34*mm, 45*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += self.line_spacer()
        elems += self.line_spacer()
        elems += self.line_spacer()

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Driver Information - attach schedule if over 5 drivers", styles["rc-white-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-pdfdivider-table"], [
                ]),
                rowHeights=(7*mm),
                colWidths=(204*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Name", styles["rc-blue-text"]),
                        Paragraph("Date of <br/>Birth", styles["rc-blue-text"]),
                        Paragraph("State", styles["rc-blue-text"]),
                        Paragraph("Driver's License <br/>Number", styles["rc-blue-text"]),
                        Paragraph("Date of <br/>Hire", styles["rc-blue-text"]),
                        Paragraph("CDL (yes <br/>or no)", styles["rc-blue-text"]),
                        Paragraph("Years of Experience <br/>Using Scheduled <br/>Equipment", styles["rc-blue-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("GRID", (0, 0), (-1, -1), .45, "black"),
                	("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]),
                colWidths=(40*mm, 20*mm, 15*mm, 40*mm, 20*mm, 24*mm, 45*mm),
                rowHeights=(17*mm)
            ),
        ]

        elems += self.driver_information()

     	elems += self.line_spacer()
        elems += self.line_spacer()
        elems += self.line_spacer()

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Vehicle and Trailer Information - attach schedule if over 10 vehicles/trailers", styles["rc-white-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-pdfdivider-table"], [
                ]),
                rowHeights=(7*mm),
                colWidths=(204*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("VIN", styles["rc-blue-text"]),
                        Paragraph("Year", styles["rc-blue-text"]),
                        Paragraph("Make", styles["rc-blue-text"]),
                        Paragraph("Vehicle/Trailer<br/>Type", styles["rc-blue-text"]),
                        Paragraph("Garaging<br/>Zip Code", styles["rc-blue-text"]),
                        Paragraph("Maximum Distance Traveled from<br/>Garaging Location (Radius)", styles["rc-blue-text"]),
                        Paragraph("Current<br/>Value", styles["rc-blue-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("GRID", (0, 0), (-1, -1), .45, "black"),
                	("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]),
                colWidths=(44*mm, 12*mm, 25*mm, 30*mm, 25*mm, 53*mm, 15*mm),
                rowHeights=(17*mm)
            ),
        ]

        elems += self.vehicle_trailer()

        elems += [ PageBreak() ]

        elems += [
            Table(
                [
                    [
                        Paragraph(
                            "Truck Insurance Application",                
                            extend_style(styles["rc-pdf-header"])
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                rowHeights=12.4 * mm
            ),
        ]

        elems += [Spacer(width=0, height=10)]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Liability and Cargo Coverage", styles["rc-white-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-pdfdivider-table"], [
                ]),
                rowHeights=(7*mm),
                colWidths=(204*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Type of Cargo Hauled", styles["rc-blue-text"]),
                        Paragraph("% of Total Cargo", styles["rc-blue-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("GRID", (0, 0), (-1, -1), .45, "black"),
                	("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]),
                colWidths=(110*mm, 94*mm),
                rowHeights=(10*mm)
            ),
        ]

        elems += self.cargo_hauled()

        elems += [Spacer(width=0, height=10)]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Owner, Partner and Managers Information", styles["rc-white-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-pdfdivider-table"], [
                ]),
                rowHeights=(7*mm),
                colWidths=(204*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Full Name", styles["rc-blue-text"]),
                        Paragraph("Date of Birth", styles["rc-blue-text"]),
                        Paragraph("Mailing Address", styles["rc-blue-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("GRID", (0, 0), (-1, -1), .45, "black"),
                	("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]),
                colWidths=(65*mm, 45*mm, 94*mm),
                rowHeights=(10*mm)
            ),
        ]

        elems += self.owners_block()

        elems += [Spacer(width=0, height=10)]

        elems += [
            Table(
                [
                    [ 
                        Paragraph("Additional Questions", styles["rc-white-text"]),
                    ]
                ],
                style=extend_table_style(styles["rc-pdfdivider-table"], [
                ]),
                rowHeights=(7*mm),
                colWidths=(204*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('Do you pull double trailers?', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('Do you pull triple trailers?', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('Do you plan on adding any additional drivers?', styles["rc-main-content"]),
                        self.underline(),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(40*mm, 20*mm, 37*mm, 20*mm, 66*mm, 21*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('What BI & PD Limits are you looking for?', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('What Cargo Coverage Limits are you looking for?', styles["rc-main-content"]),
                        self.underline(),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(60*mm, 25*mm, 71*mm, 25*mm, 23*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('If plan to hire, what are the minimum Years of Commercial Driving experience required?', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('CDL years required?', styles["rc-main-content"]),
                        self.underline(),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(125*mm, 23*mm, 32*mm, 24*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('If plan to hire, are vehicles Owner-driven only?', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('Do you order MVRs on all drivers prior to Hiring?', styles["rc-main-content"]),
                        self.underline(),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(67*mm, 23*mm, 70*mm, 21*mm, 23*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('Do you Agree to report all newly hired operators?', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('Do you lease your authority?', styles["rc-main-content"]),
                        self.underline(),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(70*mm, 23*mm, 42*mm, 21*mm, 48*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('Do you operate as a subsidiary of a different company?', styles["rc-main-content"]),
                        self.underline(),
                        Paragraph('Have you ever changed your operating name?', styles["rc-main-content"]),
                        self.underline(),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(79*mm, 23*mm, 67*mm, 21*mm, 14*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('Does our policy cover all vehicles owned operated or leased to the Business?', styles["rc-main-content"]),
                        self.underline(),
                        None
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(110*mm, 23*mm, 71*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [Spacer(width=0, height=30)]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('COMMENTS', styles["rc-main-content"]),
                        self.underline(self.company['comments']),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(20*mm, 184*mm),
            ),
        ]

        elems += [PageBreak()]

        elems += [
            Table(
                [
                    [
                        Paragraph(
                            "Truck Insurance Application",                
                            extend_style(styles["rc-pdf-header"])
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]),
                rowHeights=12.4 * mm
            ),
        ]

        elems += [Spacer(width=0, height=10)]

        elems += [
        	Paragraph("No coverage is bound until the Company (LuckyTruck, Inc.) advises the Applicant or its representative that a policy will be issued and then only as of the policy effective date and in accordance with all policy terms. The Applicant acknowledges that the Applicant's Representative named below is acting as Applicant's agent and not on behalf of the Company. The Applicant's Representative has no authority to bind coverage, may not accept any funds for the Company, and may not modify or interpret the terms of the policy. The Applicant agrees that the foregoing statements and answers are true and correct. The Applicant requests the Company to rely on its statements and answers in issuing any policy or subsequent renewal. The Applicant agrees that if its statements and answers are materially false, the Company may deny a claim on any policy or subsequent renewal it may issue. If any jurisdiction in which the Applicant intends to operate or the Federal Highway Administration requires a special endorsement to be attached to the policy which increases the Company's liability, the Applicant agrees to reimburse the Company in accordance with the terms of that endorsement. The Applicant agrees that any inspection of autos, vehicles, equipment, premises, operations, or inspection of any other matter relating to insurance that may be provided by the Company, is made for the use and benefit of the Company only, and is not to be relied upon by the Applicant or any other party in any respect. The Applicant understands that an inquiry may be made into the character, finances, driving records, and other personal and business background information the Company deems necessary in determining whether to bind or maintain coverage. Upon written request, additional information will be provided to the Applicant regarding any investigation. The Applicant represents that she/he has completed all relevant sections of this Application prior to execution and that the Applicant has personally signed below (or if Applicant is a Corporation, a corporate officer has signed below).",                
                            extend_style(styles["rc-long-content"]))
        ]

        elems += [Spacer(width=0, height=35)]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('If premium financed, please list provider', styles["rc-main-content"]),
                        self.underline(),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(57*mm, 145*mm),
                rowHeights=(7*mm)
            ),
        ]

        elems += [Spacer(width=0, height=40)]

        elems += [
            Table(
                [
                    [ 
                        Paragraph('A PERSON WHO KNOWINGLY AND WITH INTENT TO INJURE, DEFRAUD, OR DECEIVE AN INSURANCE COMPANY FILES A CLAIM CONTAINING FALSE, INCOMPLETE, OR MISLEADING INFORMATION MAY BE PROSECUTED UNDER STATE LAW.', styles["rc-bold-header"]),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                	("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                rowHeights=(7*mm)
            ),
        ]

        elems += [
        	 Table(
                [
                    [  
			        	Table(
			                [
			                    [   
			                        Paragraph("<img src='{}' width='220' height='55'/>".format(self.signature), extend_style(styles["rc-underline-text"])),
			                    ],
			                    [   
			                        Paragraph("Applicant's Signature", extend_style(styles["rc-underline-text1"])),
			                    ],
			                ],
			                style=extend_table_style(styles["rc-main-table"], [
			                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
			                    ("LINEABOVE", (0, -1), (-1, -1), 0.75, 'black')
			                ]),
			                colWidths=(102*mm),
			                rowHeights=(6*mm)
			            ),
			            None,
                        Table(
                            [
                                [   
                                    Paragraph(date.now().strftime('%y-%d-%m %H:%M:%S'), extend_style(styles["rc-normal-text"])),
                                ],
                                [   
                                    Paragraph("Date", extend_style(styles["rc-underline-text1"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LINEABOVE", (0, -1), (-1, -1), 0.75, 'black')
                            ]),
                            colWidths=(50*mm),
                            rowHeights=(6*mm)
                        ),
                        None
		         	]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]),
                colWidths=(102*mm, 5*mm, 62*mm, 30*mm),
                rowHeights=40*mm
            )                        
        ]

        elems += [
        	Table(
                [
                    [   
                        Paragraph("Request to Company General Agent:", extend_style(styles["rc-blue-text1"])),
                    ],
                    [   
                        Table(
			                [
			                    [   
			                        self.checkbox_text('Please quote', 25),
			                        None,
			                        self.checkbox_text('Please bind at the earliest possible date and issue policy', 165),
			                    ],
			                ],
			                style=extend_table_style(styles["rc-main-table"], [
			                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
			                ]),
			                colWidths=(25*mm, 10*mm, 165*mm),
			                rowHeights=(6*mm)
			            ),
                    ],
                    [   
                        Table(
			                [
			                    [   
			                        self.checkbox_text('Please issue policy effective', 40),
			                        self.underline(),
			                        Paragraph("Coverage was bound by", extend_style(styles["rc-main-content"])),
			                        self.underline(),
			                        None
			                    ],
			                ],
			                style=extend_table_style(styles["rc-main-table"], [
			                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
			                ]),
			                colWidths=(40*mm, 35*mm, 40*mm, 31*mm, 30*mm,),
			                rowHeights=(6*mm)
			            ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (-1, -1), (-1, -1), 5),
                    ("BOX", (0, 0), (-1, -1), 0.75, '#5f98f8')
                ]),
                rowHeights=(6*mm)
            ),
        ]

        return elems