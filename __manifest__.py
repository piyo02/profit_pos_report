{
    'name': 'Profit PoS Report',
    'author': "TechnoIndo",
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Profit PoS Report.',
    'description': '''Profit PoS Report'''
                   ,
    'depends': ['base', 'point_of_sale'],
    'data': [
        'report/pos_report_temp.xml',
        'report/pos_temp.xml',
        'wizard/profit_wizard.xml',
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
