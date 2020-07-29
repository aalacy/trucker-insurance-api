# -*- coding: utf-8 -*-
import cStringIO
from datetime import datetime as date
import json

from document_specific_styles import *
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Flowable, Paragraph, Table, Spacer, PageBreak

L_S = 2.2 

def nico(title='nico.pdf', author="Luckytruck", company={}):
    cr =ROCReport(title=title, company=company)
    buff = cStringIO.StringIO()
    page_count = cr.get_page_count(buff)    
    return cr.create_report(buff, page_count)

class ROCReport:
    BASE_PATH = os.path.abspath(os.curdir) + '/routes/coi'

    def __init__(self, title=None, author="Luckytruck", company=None):
        self.page_size = letter
        self.page_margin = (7 * mm, 6.4 * mm)
        self.sections = ["header", "content"]
        self.title = title
        self.author = author
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
        self.cargo_hauled_list = json.loads(company['cargoHauled'])
        self.vehicles_trailers_list = json.loads(company['vehicleInformationList'])['vehicle'] + json.loads(company['vehicleInformationList'])['trailer']
        self.signature = json.loads(company['signSignature']).get('imageSign', '')
        self.nico_questions = json.loads(company['nico_questions'])    

    def get_cargo_haulded(self):
        hauled = ''
        for key, value in self.cargo_hauled_list.items():
            hauled += key + ': ' + ','.join(value) + ' - '

        return hauled

    def check_business_type(self, type):
        if type in self.business_structure:
            return True
        else:
            return False

    def _26_ques(self, ques):
        mark = 'No'
        # _ques = nico_tuple[ques]
        if self.nico_questions.get(ques, False):
            mark = 'Yes'

        return mark

    def _select_type(self, ques):
        if self.nico_questions.get('You want broad form peril coverage for cargo (if you need cargo).') and ques == 'Broad Form':
            return 'x'
        elif not self.nico_questions.get('You want broad form peril coverage for cargo (if you need cargo).') and ques == 'Named Perils':
            return 'x'

    def title_policy_term_from(self):
        return self.formatDate('policyEffectiveDate') + ' To ' + self.formatDate('policyExpirationDate')

    def _get_lines(self, description, begin_idx=0, font='Arial', font_size=8):
        w_temp = description.split(' ')
        word_list = []
        for word in w_temp:
            if word != '':
                word_list.append(word)
        lines = []
        idx = 0        
        while idx <= len(word_list):
            line = ' '.join(word_list[begin_idx:idx])
            t_len = stringWidth(line, "Times-Roman", 10)
            if t_len > 645.0:                
                if t_len > 648.0:
                    line = ' '.join(word_list[begin_idx:idx-1])
                    begin_idx = idx-1
                else:
                    begin_idx = idx
                lines += [
                    Table(
                        [
                            [
                                Paragraph(line, styles["rc-normal-text"])
                            ]
                        ],
                        style=extend_table_style(styles["rc-main-table"], [
                            ("TOPPADDING", (0, 0), (-1, -1), 3),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LINEBELOW", (0, 0), (-1, -1), .45, "black"),
                        ]),
                    )
                ]
            idx += 1
        lines += [
            Table(
                [
                    [
                        Paragraph(line, styles["rc-normal-text"])
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, -1), .45, "black"),
                ]),
            )
        ]

        return lines

    def get_lines(self, idx, begin_idx=0, font='Arial', font_size=8):
        description = self.nico_questions[idx].replace('\n','').replace('\t', '')
        return self._get_lines(description, begin_idx, font, font_size)

    def _partial_text(self, description, width, font='Arial', font_size=8):
        w_temp = description.split(' ')
        word_list = []
        for word in w_temp:
            if word != '':
                word_list.append(word)
        lines = []
        begin_idx = 0
        idx = 0   
        is_continued = False     
        while idx <= len(word_list):
            line = ' '.join(word_list[begin_idx:idx])
            t_len = stringWidth(line, font, font_size)
            if t_len > width*2.8-3:                
                if t_len > width*2.8:
                    line = ' '.join(word_list[begin_idx:idx-1])
                    begin_idx = idx-1
                else:
                    begin_idx = idx
                
                is_continued = True
                break

            idx += 1

        return line, idx-1, is_continued

    def partial_text(self, idx, width, font='Arial', font_size=8):
        return self._partial_text(self.nico_questions[idx], width, font, font_size)

    def formatDate(self, val):
        value = ''
        try:
            _val = date.strptime(self.nico_questions[val], '%Y-%m-%d')
            value = _val.strftime('%m/%d/%Y')
        except:
            pass

        return value

    def validate(self, val):
        if val:
            return val.strip()
        else:
            return ""

    def get_page_count(self, buff=None):
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
                bottomPadding=0,
                rightPadding=0,
                topPadding=0,
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
        return doc_t.page


    def create_report(self, buff=None, page_count=None):
        def page_number(canv, doc):
            page_num = Table(
                [
                    [   
                       Paragraph("M-4467d VA (12/2007)", extend_style(styles["rc-bold-text"])),
                       Paragraph("Truck Application Page {} of {}".format(str(doc.page), page_count), extend_style(styles["rc-normal-end"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                ]),
                colWidths=(90*mm, 122*mm),
                rowHeights=6*mm
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
                                    Paragraph(self.title_policy_term_from(), styles["rc-medium-content"]),
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

    def yes_no(self, mark=None):
        return Table(
            [
                [
                    self.checkbox(size='small', checked=mark=='Yes'),
                    Paragraph("Yes", styles["rc-checkbox-text-small"]),
                    self.checkbox(size='small', checked=mark=='No'),
                    Paragraph("No", styles["rc-checkbox-text-small"]),
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]),
            colWidths=(3*mm, 8*mm, 3*mm, 7*mm),
        )

    def checkbox_text(self, text, width, bold=False, checked=None):
        text_style = "rc-checkbox-text-small"
        if bold:
            text_style = "rc-bold-text"
        return Table(
            [
                [
                    self.checkbox(size='small', checked=checked),
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

    def underline(self, text=""):
        return  Table(
                    [
                        [ 
                            Paragraph(text, styles["rc-normal-text"]),
                        ]
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LINEBELOW", (0, 0), (-1, -1), .45, "black"),
                    ]),
                )

    def driver_information(self):
        drivers = []
        for number in range(0, 5):
            if number >= len(self.drivers_information_list):
                driver = {
                    'firstName': '',
                    'lastName': '',
                    'dob': '',
                    'doh': '',
                    'address': '',
                    'state': '',
                    'city': '',
                    'zip': '',
                    'licenseNumber': '',
                    'CDL': '',
                    'dlYearLicensed': '',
                    'typeOfUnit': '',
                    'noOfYearsDriving': '',
                }
            else:
                driver = self.drivers_information_list[number]

            drivers.append(
                Table(
                    [
                        [   
                           Paragraph(str(number+1)+'. '+driver['firstName'] + ' ' + driver['lastName'], extend_style(styles["rc-normal-text"])),
                           Paragraph(driver['dob'], extend_style(styles["rc-normal-text"])),
                           Paragraph(str(driver['state']), extend_style(styles["rc-normal-text"])),
                           Paragraph(str(driver['licenseNumber']), extend_style(styles["rc-normal-text"])),
                           Paragraph(str(driver['CDL']), extend_style(styles["rc-normal-text"])),
                           Paragraph(driver['dlYearLicensed'], extend_style(styles["rc-normal-text"])),
                           Paragraph(driver['typeOfUnit'], extend_style(styles["rc-normal-text"])),
                           Paragraph(driver['noOfYearsDriving'], extend_style(styles["rc-normal-text"])),
                        ]
                    ],
                    style=extend_table_style(styles["rc-main-table"], [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), .15, "black"),
                    ]),
                    colWidths=(60*mm, 20*mm, 10*mm, 39*mm, 20*mm, 25*mm, 20*mm, 8*mm),
                    rowHeights=4*mm
                ),
            )

        return drivers

    def driver_information_continued(self):
        drivers_continue = []
        for number in range(0, 5):
            if number >= len(self.drivers_information_list):
                driver = {
                    'doh': '',
                    'prevCDE': '',
                    'noOfAccidents': '',
                    'noOfAccidentsDate': '',
                    'noOfViolations': '',
                    'noOfViolationsDate': '',
                    'conviction': '',
                    'convictionDate': '',
                    'EICOOF': '',
                }
            else:
                driver = self.drivers_information_list[number]

            drivers_continue.append(Table(
                [
                    [   
                       Paragraph("{}.&nbsp;&nbsp;&nbsp;{}".format(number+1, driver['prevCDE']), extend_style(styles["rc-normal-header"])),
                       Paragraph(driver['doh'], extend_style(styles["rc-normal-text"])),
                       Paragraph(driver['noOfAccidents'], extend_style(styles["rc-normal-text"])),
                       Paragraph(driver['noOfAccidentsDate'], extend_style(styles["rc-normal-text"])),
                       Paragraph(driver['noOfViolations'], extend_style(styles["rc-normal-text"])),
                       Paragraph(driver['noOfViolationsDate'], extend_style(styles["rc-normal-text"])),
                       Paragraph(driver['conviction'], extend_style(styles["rc-normal-text"])),
                       Paragraph(driver['convictionDate'], extend_style(styles["rc-normal-text"])),
                       Paragraph(driver['EICOOF'], extend_style(styles["rc-normal-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(20*mm, 22*mm, 17*mm, 22*mm, 17*mm, 22*mm, 40*mm, 20*mm, 22*mm),
            )),

        return drivers_continue

    def schedule_detail(self):
        vehicles = []
        for number in range(0, 10):
            if number >= len(self.vehicles_trailers_list):
                vehicle = {
                    'year': '',
                    'model': '',
                    'vehicleType': '',
                    'VIN': '',
                    'radiusOfTravelVehicle': '',
                    'grossVehicleWeight': '',
                    'totalRearAxles': '',
                    'garagingLocation': '',
                    'annualMileagePerVehicle': '',
                    'antilockBrakersOrAirBags': ''
                }
            else:
                vehicle = self.vehicles_trailers_list[number]

            vehicles.append(Table(
                [
                    [   
                       Paragraph(str(number+1), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['year']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['model']), extend_style(styles["rc-normal-text"])),
                       Paragraph(vehicle.get('vehicleType', ''), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['VIN']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['grossVehicleWeight']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['totalRearAxles']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['garagingLocation']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle.get('radiusOfTravelVehicle', '')), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['annualMileagePerVehicle']), extend_style(styles["rc-normal-text"])),
                       Paragraph(str(vehicle['antilockBrakersOrAirBags']), extend_style(styles["rc-normal-text"])),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(7*mm, 11*mm, 22*mm, 36*mm, 32*mm, 18*mm, 9*mm, 30*mm, 10*mm, 15*mm, 12*mm),
            ))
        return vehicles

    def physical_detail_with_values(self, number):
        return Table(
            [
                [   
                    Paragraph(number, extend_style(styles["rc-normal-header"])),
                    Paragraph(self.formatDate('Q65'), extend_style(styles["rc-normal-text"])),
                    Paragraph(self.nico_questions['Q66'], extend_style(styles["rc-normal-text"])),
                    Paragraph(self.nico_questions['Q67'], extend_style(styles["rc-normal-text"])),
                    Paragraph(self.nico_questions['Q68'], extend_style(styles["rc-normal-text"])),
                    Paragraph(self.nico_questions['Q69'], extend_style(styles["rc-normal-text"])),
                    Paragraph(self.nico_questions['Q70'], extend_style(styles["rc-normal-text"])),
                    Paragraph(self.nico_questions['Q72'], extend_style(styles["rc-normal-text"])),
                    Paragraph(self.nico_questions['Q73'], extend_style(styles["rc-normal-text"])),
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), .25, "black"),
            ]),
            colWidths=(8*mm, 21*mm, 21*mm, 32*mm, 32*mm, 22*mm, 27*mm, 19*mm, 20*mm),
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
        ),

    def loss_experience_with_value(self):
        return Table(
            [
                [   
                    Paragraph(self.formatDate('Q78'), extend_style(styles["rc-normal-center"])),
                    Paragraph(self.formatDate('Q79'), extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q80'], extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q81'], extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q82'], extend_style(styles["rc-normal-center"])),
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
        ),

    def loss_experience(self):
        return Table(
            [
                [   
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
                    None,
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), .25, "black"),
            ]),
            colWidths=(17.5*mm, 17.5*mm, 38*mm, 20*mm, 16*mm, 17.5*mm, 17.5*mm, 14.5*mm, 14.5*mm, 14.5*mm, 14.5*mm),
        ),

    def cargo_information_with_value(self):
        return Table(
            [
                [   
                    Paragraph(self.formatDate('Q94'), extend_style(styles["rc-normal-center"])),
                    Paragraph(self.formatDate('Q95'), extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q96'], extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q97'], extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q98'], extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q99'], extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q100'], extend_style(styles["rc-normal-center"])),
                    None,
                ]
            ],
            style=extend_table_style(styles["rc-main-table"], [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), .25, "black"),
            ]),
            colWidths=(17.5*mm, 17.5*mm, 48*mm, 20*mm, 16*mm, 35*mm, 23*mm, 25*mm),
        ),

    def cargo_information(self):
        return Table(
            [
                [   
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
            colWidths=(17.5*mm, 17.5*mm, 48*mm, 20*mm, 16*mm, 35*mm, 23*mm, 25*mm),
        ),

    def describe_cargo_with_value(self):
        return  Table(
            [
                [   
                    None,
                    Paragraph("", extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q102'], extend_style(styles["rc-normal-center"])),
                    Paragraph(self.nico_questions['Q101'], extend_style(styles["rc-normal-center"])),
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
                                Paragraph(self.nico_questions['Q36'], extend_style(styles["rc-normal-center"])),
                                Paragraph(self.nico_questions['Q37_1'], extend_style(styles["rc-normal-center"])),
                                Paragraph(self.nico_questions['Q37_2'], extend_style(styles["rc-normal-center"])),
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
        name_dba = self.name
        if self.dba:
            name_dba += '({})'.format(self.dba)   
        elems = [
            Table(
                [
                    [   
                        self.right_header("1."),
                        Paragraph('Name (and "dba")', extend_style(styles["rc-first-label"])),
                        self.underline(name_dba)
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
                        self.checkbox(size='small', checked='Proprietorship' in self.business_structure),
                        Paragraph("Individual / Proprietorship", styles["rc-checkbox-text-small"]),
                        self.checkbox(size='small', checked='Partnership' in self.business_structure),
                        Paragraph("Partnership", styles["rc-checkbox-text-small"]),
                        self.checkbox(size='small', checked='Corporation' in self.business_structure),
                        Paragraph("Corporation", styles["rc-checkbox-text-small"]),
                        self.checkbox(size='small', checked='Limited Liability Company' in self.business_structure),
                        Paragraph("Other", styles["rc-checkbox-text-small"]),
                        Paragraph("Business Phone Number", extend_style(styles["rc-first-label"])),
                        Table(
                            [
                                [ 
                                    self.underline(self.phone_number)
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
                        self.underline(self.mailing_address['address']),
                        Paragraph("City", extend_style(styles["rc-first-label"])),
                        self.underline(self.mailing_address['city']),
                        Paragraph("State", extend_style(styles["rc-first-label"])),
                        self.underline(self.mailing_address['state']),
                        Paragraph("Zip", extend_style(styles["rc-first-label"])),
                        self.underline(self.mailing_address['zip'])
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
                        self.underline(self.garaging_addr['address']),
                        Paragraph("City", extend_style(styles["rc-first-label"])),
                        self.underline(self.garaging_addr['city']),
                        Paragraph("State", extend_style(styles["rc-first-label"])),
                        self.underline(self.garaging_addr['state']),
                        Paragraph("Zip", extend_style(styles["rc-first-label"])),
                        self.underline(self.garaging_addr['zip'])
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
                        self.underline(self.nico_questions['contactName'] + ' ' + self.nico_questions['phoneNumber'])
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
                        self.yes_no(self._26_ques('Q5')),
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
                        self.underline(self.nico_questions['Q6_policyNumber']),
                        Paragraph("Effective Date(s)", extend_style(styles["rc-first-label"])),
                        self.underline(self.formatDate('Q6_policyNumberEffectiveDate'))
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
                        self.underline(self.partial_text('Q7', 172)[0])
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 25 * mm, 172 * mm),
            )]

        if self.partial_text('Q7', 172)[2]:
            elems += self.get_lines('Q7', self.partial_text('Q7', 172)[1])

        elems += [    
            Table(
                [
                    [   
                        None,
                        Paragraph("Years experience", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['yearsExperience']),
                        Paragraph("New Venture?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q9')),
                        Paragraph("If you are a low truck operation, do you do repossessions?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q10')),
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
                        self.yes_no(self._26_ques("Q11_0")),
                        Paragraph("If no, explain", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q11', 110)[0])
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 42 * mm, 25*mm, 20*mm, 110 * mm),
            )]

        if self.partial_text('Q11', 110)[2]:
            elems += self.get_lines('Q11', self.partial_text('Q11', 110)[1])

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("Seasonal?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q12')),
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
                        self.yes_no(self._26_ques("Q13_0")),
                        Paragraph("If yes, when", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q13']),
                        Paragraph("Explain", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q14', 78)[0])
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 5 * mm, 48 * mm, 23*mm, 18*mm, 17*mm, 13*mm, 78*mm),
            ),
        ]

        if self.partial_text('Q14', 78)[2]:
            elems += self.get_lines('Q14', self.partial_text('Q14', 78)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("9."),
                        Paragraph("Gross receipts last year", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q15']),
                        Paragraph("Estimate for coming year", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q16']),
                        Paragraph("Business for sale?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q17')),
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
                        self.yes_no(self._26_ques('Q18')),
                        Paragraph("If yes, list states", extend_style(styles["rc-first-label"])),
                        self.underline(','.join(self.nico_questions['Q19'])),
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
                        self.yes_no(self._26_ques("Q20_0")),
                        Paragraph("Show largest cities entered", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q20']),
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
                        self.yes_no(self._26_ques('Q21')),
                        Paragraph("If yes, show towns operated between", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q22', 69)[0]),
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

        if self.partial_text('Q22', 69)[2]:
            elems += self.get_lines('Q22', self.partial_text('Q22', 69)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("13."),
                        Paragraph("Are you a common carrier?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q23_0")),
                        Paragraph("Are you a contract hauler?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q23_1")),
                        Paragraph("If yes, for whom", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q23', 45)[0]),
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

        if self.partial_text('Q23', 45)[2]:
            elems += self.get_lines('Q23', self.partial_text('Q23', 45)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("14."),
                        Paragraph("List all types of cargo hauled", extend_style(styles["rc-first-label"])),
                        self.underline(self._partial_text(self.get_cargo_haulded(), 156)[0]),
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

        if self._partial_text(self.get_cargo_haulded(), 156)[2]:
            elems += self._get_lines(self.get_cargo_haulded(), self._partial_text(self.get_cargo_haulded(), 156)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("15."),
                        Paragraph("Do you haul any hazardous or extra hazardous substances or materials as defined by EPA?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q24_0")),
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
                        self.underline(self.partial_text('Q24', 130)[0]),
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

        if self.partial_text('Q24', 130)[2]:
            elems += self.get_lines('Q24', self.partial_text('Q24', 130)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("16."),
                        Paragraph("Do you haul your own cargo exclusively?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q25_0")),
                        Paragraph("If not, who owns it?", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q25', 91)[0]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
                ]),
                colWidths=( 6 * mm, 56*mm, 21*mm, 28*mm, 91*mm),
            ),
        ]

        if self.partial_text('Q25', 91)[2]:
            elems += self.get_lines('Q25', self.partial_text('Q25', 91)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("17."),
                        Paragraph("Do you pull double trailer?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q25_17_1")),
                        Paragraph("Triple trailer?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q25_17_2")),
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
                        self.yes_no(self._26_ques("Q26_0")),
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
                        self.yes_no(self._26_ques('Q27')),
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
                                                Paragraph(self.nico_questions['Q30'], extend_style(styles["rc-normal-center"])),
                                                Paragraph(self.nico_questions['Q31_1'], extend_style(styles["rc-normal-center"])),
                                                Paragraph(self.nico_questions['Q31_2'], extend_style(styles["rc-normal-center"])),
                                                Paragraph(self.nico_questions['Q32'], extend_style(styles["rc-normal-center"]))
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
                                                            Paragraph(self.nico_questions['Q33'], extend_style(styles["rc-normal-center"]))
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
                                                            Paragraph(self.nico_questions['Q34'], extend_style(styles["rc-normal-center"]))
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
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(18*mm) 
            ),
        ]

        elems += [
            Table(
                [   
                    [
                        self.driver_information()
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(20*mm) 
            ),
        ]

        # elems += [PageBreak()]

        elems += self.line_spacer()

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
        ]

        elems += [
            Table(
                [
                    [
                        self.driver_information_continued()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                # rowHeights=(22.5*mm)
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
                        Paragraph("Are drivers covered by workers compensation?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q49_0")),
                        Paragraph("If yes, name of carrier?", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q49']),
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
                        self.underline(self.nico_questions['Q50']),
                        None,
                        Paragraph("Are vehicles owner-driven only?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q51')),
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
                        self.yes_no(self._26_ques("Q51_22_1")),
                        Paragraph("If yes, will family members drive?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q51_22_2")),
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
                        Paragraph("Do you order MVRs on all drivers prior to hiring?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques("Q52_0")),
                        Paragraph("Drivers maximum driving hours", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q52_daily']),
                        Paragraph("daily,", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q52_weekly']),
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
                        self.yes_no(self._26_ques("Q52_24")),
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
                        self.checkbox_text(text="Hourly", width=17, checked=self.nico_questions['Q53']=='Hourly'),
                        self.checkbox_text(text="Trip", width=11, checked=self.nico_questions['Q53']=='Trip'),
                        self.checkbox_text(text="Mileage", width=25, checked=self.nico_questions['Q53']=='Mileage'),
                        self.checkbox_text(text="Other,", width=12, checked=self.nico_questions['Q53']=='Other'),
                        Paragraph("Explain", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q53_explain', 62)[0])
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

        if self.partial_text('Q53_explain', 62)[2]:
            elems += self.get_lines('Q53_explain', self.partial_text('Q53_explain', 62)[1])

        elems += self.line_spacer()

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
                            colWidths=(7*mm, 11*mm, 22*mm, 36*mm, 32*mm, 18*mm, 9*mm, 30*mm, 10*mm, 15*mm, 12*mm),
                            rowHeights=(18*mm)
                        ),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=(202*mm),
                rowHeights=(18*mm)
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.schedule_detail()
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), .75, "black"),
                ]),
                colWidths=( 202*mm),
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("26."),
                        Paragraph("Will lessor be added as additional insured?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q60')),
                        Paragraph("If yes, give me name and address of lessor of each vehicle", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q61', 37)[0]),
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

        if self.partial_text('Q61', 37)[2]:
            elems += self.get_lines('Q61', self.partial_text('Q61', 37)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("27."),
                        Paragraph("Number of vehicles owned:", extend_style(styles["rc-first-label"])),
                        Paragraph("Pick-Ups", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q62_pick_ups'])),
                        Paragraph("Trucks", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q62_trucks'])),
                        Paragraph("Tractors", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q62_tractors'])),
                        Paragraph("Semi-Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q62_semi_trailers'])),
                        Paragraph("Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q62_trailers'])),
                        Paragraph("Pup-Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q62_pup_trailers'])),
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
                        self.underline(str(self.nico_questions['Q63_pick_ups'])),
                        Paragraph("Trucks", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q63_trucks'])),
                        Paragraph("Tractors", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q63_tractors'])),
                        Paragraph("Semi-Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q63_semi_trailers'])),
                        Paragraph("Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q63_trailers'])),
                        Paragraph("Pup-Trailers", extend_style(styles["rc-first-label"])),
                        self.underline(str(self.nico_questions['Q63_pup_trailers'])),
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
                    ],
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
            ),
        ]

        elems += [
            Table(
                [   
                    [   
                        self.physical_detail_with_values("1.")
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
            ),
        ]

        elems += [
            Table(
                [
                    [   
                        self.right_header("29."),
                        Paragraph("Any loss payees?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q74')),
                        Paragraph("If yes, give me name and address of mortgagee/loss of each vehicle", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q75', 58)[0]),
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

        if self.partial_text('Q75', 58)[2]:
            elems += self.get_lines('Q75', self.partial_text('Q75', 58)[1])

        # elems += [
        #     Table(
        #         [
        #             [   
        #                 None,
        #                 self.underline(),
        #             ]
        #         ],
        #         style=extend_table_style(styles["rc-main-table"], [
        #             ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        #             ("TOPPADDING", (0, 0), (-1, -1), L_S),
        #         ]),
        #         colWidths=( 7*mm, 195*mm ),
        #         rowHeights=5*mm
        #     ),
        # ]

        # elems += [ PageBreak() ]

        elems += self.line_spacer()

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
                        self.loss_experience_with_value()
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
                        self.yes_no(self._26_ques('Q89')),
                        Paragraph("If yes, provide complete details", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q90', 93)[0]),
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

        if self.partial_text('Q90', 93)[2]:
            elems += self.get_lines('Q90', self.partial_text('Q90', 93)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("31."),
                        Paragraph("Have you ever been declined, cancelled or non-renewed for this kind of insurance?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q91')),
                        Paragraph("If yes, date and why", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q92', 35)[0]),
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

        if self.partial_text('Q92', 35)[2]:
            elems += self.get_lines('Q92', self.partial_text('Q92', 35)[1])

        elems += self.line_spacer()

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
                        self.cargo_information_with_value()
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
                                    self.describe_cargo_with_value()
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
                                    self.checkbox_text('$500', 12, checked=self.nico_questions['Q103']=='$500'),
                                    None,
                                ],
                                [   
                                    None,
                                    self.checkbox_text('$1,000', 12, checked=self.nico_questions['Q103']=='$1,000'),
                                    None,
                                ],
                                [   
                                    None,
                                    self.checkbox_text('$2,500', 12, checked=self.nico_questions['Q103']=='$2,500'),
                                    None,
                                ],
                                [   
                                    None,
                                    self.checkbox_text('Other', 12, checked=self.nico_questions['Q103']=='Other'),
                                    self.underline(self.nico_questions['Q103_other']),
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
                        Paragraph("Select Type of Coverage Desired:", extend_style(styles["rc-first-label"])),
                        self.checkbox_text("Named Perils or", 24, checked=self.nico_questions['Q104']=='Named Perils'),
                        self.checkbox_text("Broad Form", 18, checked=self.nico_questions['Q104']=='Broad Form'),
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
                        self.checkbox_text("Additional Insured Endorsement (Lessee)", 55, checked=self.nico_questions['Q105']=='Additional Insured Endorsement (Lessee)'),
                        self.checkbox_text("Loading and Unloading Coverage", 55, checked=self.nico_questions['Q105']=='Loading and Unloading Coverage'),
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
                        self.checkbox_text("Earned Freight Coverage", 40, checked=self.nico_questions['Q105']=='Earned Freight Coverage'),
                        self.checkbox_text("Refrigeration Breakdown Coverage", 50, checked=self.nico_questions['Q105']=='Refrigeration Breakdown Coverage'),
                        self.checkbox_text("Hired Car Cargo Coverage", 35, checked=self.nico_questions['Q105']=='Hired Car Cargo Coverage'),
                        self.checkbox_text("Exclude Theft Coverage", 35, checked=self.nico_questions['Q105']=='Exclude Theft Coverage'),
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
                        self.yes_no(self._26_ques('Q107')),
                        Paragraph("If yes, MC number", extend_style(styles["rc-first-label"])),
                        self.underline(self.nico_questions['Q108']),
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
                        self.checkbox_text("Common", 14, checked=self.nico_questions['Q109']=='Common'),
                        self.checkbox_text("Contract", 12, checked=self.nico_questions['Q109']=='Contract'),
                        self.checkbox_text("Broker", 35, checked=self.nico_questions['Q109']=='Broker'),
                        Paragraph("Do you require FHWA cargo filing?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q110'))
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
                        self.underline(self.partial_text('Q111', 38)[0]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 158*mm, 38*mm),
                rowHeights=4*mm
            ),
        ]

        if self.partial_text('Q111', 38)[2]:
            elems += self.get_lines('Q111', self.partial_text('Q111', 38)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("36."),
                        Paragraph("If you are interstate regulated carrier, identify your registration or base state", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q112', 98)[0]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 98*mm, 98*mm),
                rowHeights=4*mm
            ),
        ]

        if self.partial_text('Q112', 98)[2]:
            elems += self.get_lines('Q112', self.partial_text('Q112', 98)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("37."),
                        Paragraph("Is an intrastate filing needed?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q113')),
                        Paragraph("If yes, show state and permit number", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q114', 81)[0]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 40*mm, 25*mm, 50*mm, 81*mm),
                rowHeights=4*mm
            ),
        ]

        if self.partial_text('Q114', 81)[2]:
            elems += self.get_lines('Q114', self.partial_text('Q114', 81)[1])

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("List states for which insured requires CARGO FILINGS (check name on permits)", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q115', 88)[0]),
                    ]
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=( 6*mm, 108*mm, 88*mm),
                rowHeights=4*mm
            ),
        ]

        if self.partial_text('Q115', 88)[2]:
            elems += self.get_lines('Q115', self.partial_text('Q115', 88)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("38."),
                        Paragraph("Show exact name and address in which permits are issued", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q116', 116)[0]),
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

        if self.partial_text('Q116', 116)[2]:
            elems += self.get_lines('Q116', self.partial_text('Q116', 116)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("39."),
                        Paragraph("Is MCS 90 endorsement needed?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q117')),
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
                        self.yes_no(self._26_ques('Q118')),
                        Paragraph("If yes, explain", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q119', 49)[0])
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

        if self.partial_text('Q119', 49)[2]:
            elems += self.get_lines('Q119', self.partial_text('Q119', 49)[1])

        elems += [
            Table(
                [
                    [   
                        self.right_header("41."),
                        Paragraph("Are oversize, overweight commodities hauled?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q120')),
                        Paragraph("If filing required, show states", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q121', 66)[0])
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

        if self.partial_text('Q121', 66)[2]:
            elems += self.get_lines('Q121', self.partial_text('Q121', 66)[1])

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("Are escort vehicles towed on return trips?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q122')),
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
                        self.yes_no(self._26_ques('Q123')),
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
                        self.yes_no(self._26_ques('Q124')),
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
                                    self.yes_no(self._26_ques('Q124_44_1')),
                                    Paragraph("Do you operate under any other name?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(self._26_ques('Q124_44_2')),
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
                                    self.yes_no(self._26_ques('Q124_45')),
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
                                    self.yes_no(self._26_ques('Q124_46')),
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
                                    self.yes_no(self._26_ques('Q124_47_1')),
                                    Paragraph("Do you appoint agents or hire independent contractors to operate on your behalf?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(self._26_ques('Q124_47_2')),
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
                                    self.yes_no(self._26_ques('Q124_48')),
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
                                    Paragraph("Have you ever lost or had authority withdrawn, or have you been/are under probation by any regulatory authority (FHWA, PUC, etc.)?", extend_style(styles["rc-first-label"])),
                                    self.yes_no(self._26_ques('Q124_49')),
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
                                    self.yes_no(self._26_ques('Q124_50')),
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
                                    self.underline(self.partial_text('Q125', 119)[0]),
                                ]
                            ],
                            style=extend_table_style(styles["rc-square-table"], [
                            ]),
                            colWidths=( 6*mm, 79*mm, 119*mm),
                            rowHeights=4*mm
                        ),
                    ],
                    self.get_lines('Q125', self.partial_text('Q125', 119)[1])
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), L_S),
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
                        self.yes_no(self._26_ques("Q126_0")),
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
                        Paragraph("(a)  With whom has such agreement(s) been made?", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q126', 117)[0])
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

        if self.partial_text('Q126', 117)[2]:
            elems += self.get_lines('Q126', self.partial_text('Q126', 117)[1])

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("(b)  Do the parties names in (a) carry automobile liability insurance?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q127'))
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
                        self.underline(self.partial_text('Q128', 69)[0])
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

        if self.partial_text('Q128', 69)[2]:
            elems += self.get_lines('Q128', self.partial_text('Q128', 69)[1])

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("(c)  Under whose permit does each of the parties to the agreement(s) operate?", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q129', 87)[0])
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

        if self.partial_text('Q129', 87)[2]:
            elems += self.get_lines('Q129', self.partial_text('Q129', 87)[1])

        elems += [
            Table(
                [
                    [   
                        None,
                        Paragraph("(d)  Is there a hold harmless in the agreement(s)?", extend_style(styles["rc-first-label"])),
                        self.yes_no(self._26_ques('Q130'))
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
                        self.yes_no(self._26_ques("Q131_0")),
                        Paragraph("If yes, explain", extend_style(styles["rc-first-label"])),
                        self.underline(self.partial_text('Q131', 94)[0])
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

        if self.partial_text('Q131', 94)[2]:
            elems += self.get_lines('Q131', self.partial_text('Q131', 94)[1])

        elems += [PageBreak()]

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
                        Paragraph("No coverage is bound until the Company advises the Applicant or its representative that a policy will be issued and then only as of the policy effective date and in accordance with all policy terms. <b>The Apllicant acknowledges that the Applicant's Representative named below is acting as Applicant's agent and not on behalf of the Company. The Applicant's Representative has no authority to bind coverage, may not accept any funds for the Company, and may not modify or interpret the terms of the policy.</b>", extend_style(styles["rc-normal-text1"])),
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
                                   self.yes_no(self._26_ques('Q132')),
                                   Paragraph("If yes, with whome", extend_style(styles["rc-normal-text"])),
                                   self.underline(self.partial_text('Q133', 92)[0])
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ]),
                            colWidths=(45*mm, 25*mm, 30*mm, 92*mm),
                            rowHeights=5*mm
                        ),
                    ],
                ],
                style=extend_table_style(styles["rc-main-table"], [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ]),
                colWidths=(202*mm),
            ),
        ]

        if self.partial_text('Q131', 94)[2]:
            elems += self.get_lines('Q131', self.partial_text('Q131', 94)[1])

        elems += [Spacer(width=0, height=60)]

        elems += [
            Table(
                [
                    [   
                        Table(
                            [
                                [   
                                    Paragraph("", extend_style(styles["rc-small-underline"])),
                                ],
                                [   
                                    Paragraph("Witness", extend_style(styles["rc-underline-text1"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LINEABOVE", (0, -1), (-1, -1), 0.75, 'black')
                            ]),
                            colWidths=(72*mm),
                            rowHeights=(6*mm)
                        ),
                        None,
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
                            colWidths=(82*mm),
                            rowHeights=(6*mm)
                        ),
                        None,
                        Table(
                            [
                                [   
                                    Paragraph(date.now().strftime('%Y-%d-%m %H:%M:%S'), extend_style(styles["rc-normal-text"])),
                                ],
                                [   
                                    Paragraph("Date", extend_style(styles["rc-underline-text1"])),
                                ],
                            ],
                            style=extend_table_style(styles["rc-main-table"], [
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                ("LINEABOVE", (0, -1), (-1, -1), 0.75, 'black')
                            ]),
                            colWidths=(30*mm),
                            rowHeights=(6*mm)
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
                                    Paragraph("Applicant's Representative's Name and Address", extend_style(styles["rc-small-underline"])),
                                    Paragraph("Phone No.", extend_style(styles["rc-small-underline"])),
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

        return elems
