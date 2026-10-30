"""Canonical cross-category engineering reference projection.

This module does not own engineering physics.  It projects the canonical
material, coating, propellant and fluid owners and owns only reference
metadata that has no lower-level canonical owner.

Economic records here are evidence records only.  Component and total cost
calculation remains owned by cost_intelligence_owner.py.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

import material_database
import propellant_database
import fluid_property_database

from cost_intelligence_owner import (
    UNACCEPTABLE_SOURCE_QUALITIES,
)


OWNER_NAME = (
    "LEAF_ENGINEERING_REFERENCE_CATALOG"
)

REFERENCE_TYPES = frozenset({
    "PURE_COMPOUND",
    "PHASE_VARIANT",
    "MIXTURE",
    "METALLIC_ALLOY",
    "PURE_MATERIAL",
    "COATING",
})


SOURCE_REGISTRY = {'NIST_SRD69': {'authority': 'National Institute of Standards and Technology',
                'reference': 'NIST Chemistry WebBook, Standard Reference Database 69',
                'source_quality': 'PRIMARY_REFERENCE_DATABASE'},
 'MIL_DTL_25576E': {'authority': 'United States Department of Defense / DLA Energy',
                    'reference': 'MIL-DTL-25576E — Propellant, Rocket Grade Kerosene',
                    'source_quality': 'PRIMARY_GOVERNMENT_SPECIFICATION'},
 'ASTM_D1655_DLA': {'authority': 'ASTM International; DLA government cross-reference',
                    'reference': 'ASTM D1655 — Jet A aviation turbine fuel; DLA '
                                 'DSP-CS-21 cross-reference',
                    'source_quality': 'PRIMARY_STANDARD_WITH_GOVERNMENT_CROSS_REFERENCE'},
 'MIL_PRF_26539G': {'authority': 'United States Department of Defense',
                    'reference': 'MIL-PRF-26539G — Dinitrogen Tetroxide Propellant',
                    'source_quality': 'PRIMARY_GOVERNMENT_SPECIFICATION'},
 'MIL_PRF_16005F': {'authority': 'United States Department of Defense',
                    'reference': 'MIL-PRF-16005F — Propellant, Hydrogen Peroxide',
                    'source_quality': 'PRIMARY_GOVERNMENT_SPECIFICATION'},
 'SANDVIK_GRCOP42_2026': {'authority': 'Sandvik Powder Solutions',
                          'reference': 'Osprey GRCop-42 product data, updated 21 May '
                                       '2026',
                          'source_quality': 'PRIMARY_CURRENT_SUPPLIER'},
 'NASA_GRC_CU_CR_NB': {'authority': 'NASA Glenn Research Center',
                       'reference': 'NASA GRC high-conductivity Cu-Cr-Nb alloy '
                                    'literature',
                       'source_quality': 'PRIMARY_GOVERNMENT_TECHNICAL_REFERENCE'},
 'NASA_NARLOY_Z': {'authority': 'NASA Glenn Research Center',
                   'reference': 'NASA NTRS NARloy-Z literature — Cu-3 wt% Ag with '
                                'approximately 0.4-0.5 wt% Zr',
                   'source_quality': 'PRIMARY_GOVERNMENT_TECHNICAL_REFERENCE'},
 'NASA_GRCOP84': {'authority': 'NASA Glenn Research Center',
                  'reference': 'NASA NTRS — GRCop-84 high-heat-flux alloy, Cu-8 at.% '
                               'Cr-4 at.% Nb',
                  'source_quality': 'PRIMARY_GOVERNMENT_TECHNICAL_REFERENCE'},
 'HOGANAS_GLIDCOP_AL15_2025': {'authority': 'Höganäs AB',
                               'reference': 'GLIDCOP AL-15 C15715 product datasheet, '
                                            '2025',
                               'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'COPPER_ORG_C18150_2026': {'authority': 'Copper Development Association',
                            'reference': 'C18150 wrought high-copper alloy record',
                            'source_quality': 'PRIMARY_INDUSTRY_ALLOY_DATABASE'},
 'COPPER_ORG_C10100_2026': {'authority': 'Copper Development Association',
                            'reference': 'C10100 Oxygen-Free-Electronic copper record',
                            'source_quality': 'PRIMARY_INDUSTRY_ALLOY_DATABASE'},
 'SPECIAL_METALS_718_2026': {'authority': 'Special Metals Corporation',
                             'reference': 'INCONEL alloy 718 technical bulletin',
                             'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'SPECIAL_METALS_625_2026': {'authority': 'Special Metals Corporation',
                             'reference': 'INCONEL alloy 625 technical bulletin',
                             'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'HAYNES_230_2025': {'authority': 'Haynes International',
                     'reference': 'HAYNES 230 alloy nominal-composition datasheet',
                     'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'HAYNES_X_2024': {'authority': 'Haynes International',
                   'reference': 'HASTELLOY X alloy nominal-composition datasheet',
                   'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'OUTOKUMPU_STAINLESS_GRADES': {'authority': 'Outokumpu',
                                'reference': 'Outokumpu stainless-steel grades and '
                                             'typical chemical compositions',
                                'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'CARPENTER_17_4PH': {'authority': 'Carpenter Technology',
                      'reference': 'PowderRange 17-4 / UNS S17400 type analysis',
                      'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'OERLIKON_METCO_204NS': {'authority': 'Oerlikon Metco',
                          'reference': 'Metco 204NS yttria-stabilised zirconia '
                                       'thermal-spray powder',
                          'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'OERLIKON_METCO_6103': {'authority': 'Oerlikon Metco',
                         'reference': 'Metco 6103 high-purity alumina thermal-spray '
                                      'powder',
                         'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET'},
 'NIST_HAFNIUM_DIOXIDE': {'authority': 'National Institute of Standards and Technology',
                          'reference': 'NIST Chemistry WebBook SRD 69 — hafnium '
                                       'dioxide',
                          'source_quality': 'PRIMARY_REFERENCE_DATABASE'},
 'NIST_RHENIUM': {'authority': 'National Institute of Standards and Technology',
                  'reference': 'NIST Chemistry WebBook SRD 69 — elemental rhenium',
                  'source_quality': 'PRIMARY_REFERENCE_DATABASE'},
 'RAPTOR_304_FOIL_2026': {'authority': 'Raptor Supplies United Kingdom',
                          'reference': '304 stainless foil, 0.002 in × 12 in × 10 ft, '
                                       '£31.12/unit inc. VAT; retrieved 2026-08-20',
                          'source_quality': 'CURRENT_PUBLIC_RETAIL_LISTING'},
 'RAPTOR_316_BLANK_2026': {'authority': 'Raptor Supplies United Kingdom',
                           'reference': '316 stainless precision blank, 1 in × 4 in × '
                                        '12 in, 6.2775 kg, £585.94/unit inc. VAT; '
                                        'retrieved 2026-08-20',
                           'source_quality': 'CURRENT_PUBLIC_RETAIL_LISTING'},
 'RAPTOR_321_FOIL_2026': {'authority': 'Raptor Supplies United Kingdom',
                          'reference': '321 stainless foil, 0.002 in × 12 in × 10 ft, '
                                       '£52.88/unit inc. VAT; retrieved 2026-08-20',
                          'source_quality': 'CURRENT_PUBLIC_RETAIL_LISTING'},
 'SIGMA_GOODFELLOW_17_4PH_EU_2026': {'authority': 'Sigma-Aldrich / Goodfellow',
                                     'reference': 'GF58450877 — 17-4PH stainless steel '
                                                  'rod, 1000 mm × 16 mm diameter, '
                                                  'listed at EUR 488.00; retrieved '
                                                  '2026-08-20',
                                     'source_quality': 'CURRENT_PUBLIC_LAB_RETAIL_REFERENCE'},
 'SIGMA_GOODFELLOW_INCONEL625_GB_2026': {'authority': 'Sigma-Aldrich UK / Goodfellow',
                                         'reference': 'GF31550318 — Inconel 625 '
                                                      'annealed rod, 1000 mm × 6.35 mm '
                                                      'diameter, listed at GBP 451.00; '
                                                      'retrieved 2026-08-20',
                                         'source_quality': 'CURRENT_PUBLIC_LAB_RETAIL_REFERENCE'},
 'SIGMA_GOODFELLOW_HASTELLOYX_US_2026': {'authority': 'Sigma-Aldrich / Goodfellow',
                                         'reference': 'GF92879667 — Hastelloy X rod, '
                                                      '200 mm × 9.5 mm diameter, '
                                                      'listed at USD 582.00; retrieved '
                                                      '2026-08-20',
                                         'source_quality': 'CURRENT_PUBLIC_LAB_RETAIL_REFERENCE'},
 'SD_NONFERROUS_CUCRZR_UK_2026': {'authority': 'S&D Non-Ferrous Metals',
                                  'reference': 'CW106C / C18150 CuCrZr stocked in '
                                               'sheet, round, hexagon and flat-bar '
                                               'forms; supplier provides pricing by '
                                               'quotation',
                                  'source_quality': 'CURRENT_UK_SUPPLIER_QUOTE_REFERENCE'}}


PURE_SUBSTANCE_METADATA = {'METHANE': {'display_name': 'Methane',
             'chemical_formula': 'CH4',
             'molecular_weight': 16.0425,
             'cas_number': '74-82-8',
             'inchi': 'InChI=1S/CH4/h1H4',
             'source': 'NIST_SRD69',
             'structural_representation': '    H\n    |\nH — C — H\n    |\n    H'},
 'HYDROGEN': {'display_name': 'Hydrogen',
              'chemical_formula': 'H2',
              'molecular_weight': 2.01588,
              'cas_number': '1333-74-0',
              'inchi': 'InChI=1S/H2/h1H',
              'source': 'NIST_SRD69',
              'structural_representation': 'H — H'},
 'ETHANOL': {'display_name': 'Ethanol',
             'chemical_formula': 'C2H6O',
             'molecular_weight': 46.0684,
             'cas_number': '64-17-5',
             'inchi': 'InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3',
             'source': 'NIST_SRD69',
             'structural_representation': 'CH3 — CH2 — OH'},
 'METHANOL': {'display_name': 'Methanol',
              'chemical_formula': 'CH4O',
              'molecular_weight': 32.0419,
              'cas_number': '67-56-1',
              'inchi': 'InChI=1S/CH4O/c1-2/h2H,1H3',
              'source': 'NIST_SRD69',
              'structural_representation': 'CH3 — OH'},
 'MMH': {'display_name': 'Monomethylhydrazine',
         'chemical_formula': 'CH6N2',
         'molecular_weight': 46.0717,
         'cas_number': '60-34-4',
         'inchi': 'InChI=1S/CH6N2/c1-3-2/h3H,2H2,1H3',
         'source': 'NIST_SRD69',
         'structural_representation': 'CH3 — NH — NH2'},
 'UDMH': {'display_name': 'Unsymmetrical dimethylhydrazine',
          'chemical_formula': 'C2H8N2',
          'molecular_weight': 60.0983,
          'cas_number': '57-14-7',
          'inchi': 'InChI=1S/C2H8N2/c1-4(2)3/h3H2,1-2H3',
          'source': 'NIST_SRD69',
          'structural_representation': '(CH3)2N — NH2'},
 'HYDRAZINE': {'display_name': 'Hydrazine',
               'chemical_formula': 'H4N2',
               'molecular_weight': 32.0452,
               'cas_number': '302-01-2',
               'inchi': 'InChI=1S/H4N2/c1-2/h1-2H2',
               'source': 'NIST_SRD69',
               'structural_representation': 'H2N — NH2'},
 'OXYGEN': {'display_name': 'Molecular oxygen',
            'chemical_formula': 'O2',
            'molecular_weight': 31.9988,
            'cas_number': '7782-44-7',
            'inchi': 'InChI=1S/O2/c1-2',
            'source': 'NIST_SRD69',
            'structural_representation': 'O = O'},
 'NITROUS_OXIDE': {'display_name': 'Nitrous oxide',
                   'chemical_formula': 'N2O',
                   'molecular_weight': 44.0128,
                   'cas_number': '10024-97-2',
                   'inchi': 'InChI=1S/N2O/c1-2-3',
                   'source': 'NIST_SRD69',
                   'structural_representation': 'N ≡ N — O'},
 'DINITROGEN_TETROXIDE': {'display_name': 'Dinitrogen tetroxide',
                          'chemical_formula': 'N2O4',
                          'molecular_weight': 92.011,
                          'cas_number': '10544-72-6',
                          'inchi': 'InChI=1S/N2O4/c3-1(4)2(5)6',
                          'source': 'NIST_SRD69',
                          'structural_representation': 'O2N — NO2'},
 'HYDROGEN_PEROXIDE': {'display_name': 'Hydrogen peroxide',
                       'chemical_formula': 'H2O2',
                       'molecular_weight': 34.0147,
                       'cas_number': '7722-84-1',
                       'inchi': 'InChI=1S/H2O2/c1-2/h1-2H',
                       'source': 'NIST_SRD69',
                       'structural_representation': 'H — O — O — H'},
 'NITRIC_OXIDE': {'display_name': 'Nitric oxide',
                  'chemical_formula': 'NO',
                  'molecular_weight': 30.0061,
                  'cas_number': '10102-43-9',
                  'inchi': 'InChI=1S/NO/c1-2',
                  'source': 'NIST_SRD69',
                  'structural_representation': 'N — O'}}


PROPELLANT_REFERENCE_METADATA = {
    "LCH4": {
        "reference_type": "PHASE_VARIANT",
        "parent_identity": "METHANE",
        "phase": "LIQUID",
    },

    "GCH4": {
        "reference_type": "PHASE_VARIANT",
        "parent_identity": "METHANE",
        "phase": "GAS",
    },

    "LH2": {
        "reference_type": "PHASE_VARIANT",
        "parent_identity": "HYDROGEN",
        "phase": "LIQUID",
    },

    "GH2": {
        "reference_type": "PHASE_VARIANT",
        "parent_identity": "HYDROGEN",
        "phase": "GAS",
    },

    "RP-1 / Kerosene": {
        "reference_type": "MIXTURE",
        "phase": "LIQUID",
        "sources": ["MIL_DTL_25576E"],
        "composition": {
            "classification":
                "Rocket-grade kerosene hydrocarbon mixture",
        },
        "limitations": [
            "RP-1 is a specification-defined hydrocarbon mixture; "
            "a single molecular formula, atomic composition and "
            "molecular structure are not scientifically applicable.",
        ],
    },

    "Jet-A": {
        "reference_type": "MIXTURE",
        "phase": "LIQUID",
        "sources": ["ASTM_D1655_DLA"],
        "composition": {
            "classification":
                "Kerosene-type aviation turbine fuel mixture",
        },
        "limitations": [
            "Jet-A is a complex hydrocarbon fuel mixture; a single "
            "molecular formula and molecular structure are not applicable.",
        ],
    },

    "Ethanol": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "ETHANOL",
    },

    "Methanol": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "METHANOL",
    },

    "MMH": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "MMH",
    },

    "UDMH": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "UDMH",
    },

    "N2H4": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "HYDRAZINE",
    },

    "O2(L)": {
        "reference_type": "PHASE_VARIANT",
        "parent_identity": "OXYGEN",
        "phase": "LIQUID",
    },

    "O2": {
        "reference_type": "PHASE_VARIANT",
        "parent_identity": "OXYGEN",
        "phase": "GAS",
    },

    "N2O": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "NITROUS_OXIDE",
    },

    "N2O4": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "DINITROGEN_TETROXIDE",
        "limitations": [
            "This record represents the N2O4 chemical identity. "
            "Propellant-grade NTO/MON composition must be treated "
            "separately when nitric oxide is present.",
        ],
    },

    "MON3": {
        "reference_type": "MIXTURE",
        "phase": "LIQUID",
        "sources": ["MIL_PRF_26539G"],
        "composition": {
            "NITRIC_OXIDE":
                "2.5-3.0 wt%",

            "N2O4_PLUS_NO":
                ">=99.5 wt%",
        },
        "limitations": [
            "MON-3 is a specification-defined mixed oxide of "
            "nitrogen, not a single molecular species.",
        ],
    },

    "MON15": {
        "reference_type": "MIXTURE",
        "phase": "LIQUID",
        "sources": ["MIL_PRF_26539G"],
        "composition": {
            "NITRIC_OXIDE":
                "15.0-16.0 wt%",

            "N2O4_PLUS_NO":
                ">=99.5 wt%",
        },
        "limitations": [
            "MON-15 is a specification-defined mixed oxide of "
            "nitrogen, not a single molecular species.",
        ],
    },

    "MON25": {
        "reference_type": "MIXTURE",
        "phase": "LIQUID",
        "sources": ["MIL_PRF_26539G"],
        "composition": {
            "NITRIC_OXIDE":
                "25.0-26.0 wt%",

            "N2O4_PLUS_NO":
                ">=99.5 wt%",
        },
        "limitations": [
            "MON-25 is a specification-defined mixed oxide of "
            "nitrogen, not a single molecular species.",
        ],
    },

    "H2O2": {
        "reference_type": "PURE_COMPOUND",
        "parent_identity": "HYDROGEN_PEROXIDE",
        "limitations": [
            "The LEAF name H2O2 does not state a propellant-grade "
            "concentration. Chemistry fields identify the pure "
            "H2O2 substance only.",
        ],
    },

    "90_H2O2": {
        "reference_type": "MIXTURE",
        "phase": "LIQUID",
        "sources": ["MIL_PRF_16005F"],
        "composition": {
            "HYDROGEN_PEROXIDE":
                "90.0-91.5 wt%",

            "BALANCE":
                "Water plus permitted stabilizers/impurities "
                "within specification limits",
        },
        "limitations": [
            "90% H2O2 is a concentration-grade propellant mixture; "
            "it does not have a single molecular formula.",
        ],
    },

    "98_H2O2": {
        "reference_type": "MIXTURE",
        "phase": "LIQUID",
        "sources": ["MIL_PRF_16005F"],
        "composition": {
            "HYDROGEN_PEROXIDE":
                "98.0-99.0 wt%",

            "BALANCE":
                "Water plus permitted stabilizers/impurities "
                "within specification limits",
        },
        "limitations": [
            "98% H2O2 is a concentration-grade propellant mixture; "
            "it does not have a single molecular formula.",
        ],
    },
}


MATERIAL_REFERENCE_METADATA = {'GRCop-42': {'reference_type': 'METALLIC_ALLOY',
              'material_form': 'VIGA atomized additive-manufacturing powder (specific '
                               'supplier evidence)',
              'composition': {'Cu': 'Balance',
                              'Cr': '3.1-3.4 wt%',
                              'Nb': '2.7-3.0 wt%',
                              'Al': '<=0.04 wt%',
                              'Fe': '<=0.025 wt%',
                              'Si': '<=0.035 wt%',
                              'O': '<=0.05 wt%'},
              'sources': ['SANDVIK_GRCOP42_2026', 'NASA_GRC_CU_CR_NB'],
              'limitations': ['The detailed composition shown is the current Sandvik '
                              'Osprey GRCop-42 powder product specification and must '
                              'not automatically be generalized to every GRCop-42 '
                              'product form.'],
              'economic_record': {'status': 'SUPPLIER_QUOTE_REQUIRED',
                                  'unit_price_per_kg': None,
                                  'currency': None,
                                  'supplier': 'Sandvik Powder Solutions',
                                  'material_form': 'Osprey GRCop-42 metal powder',
                                  'price_source': 'SANDVIK_GRCOP42_2026',
                                  'price_date': '2026-05-21',
                                  'source_quality': 'PRIMARY_CURRENT_SUPPLIER',
                                  'reference_only': True,
                                  'not_cost_input': True,
                                  'price_basis': 'Current supplier requires quotation; '
                                                 'no public numeric £/kg value.'}},
 'NARloy-Z': {'reference_type': 'METALLIC_ALLOY',
              'material_form': 'Rocket-engine copper-alloy liner material',
              'composition': {'Cu': 'Balance',
                              'Ag': '3 wt%',
                              'Zr': 'approximately 0.4-0.5 wt% across cited NASA '
                                    'NARloy-Z literature'},
              'sources': ['NASA_NARLOY_Z'],
              'limitations': ['NASA literature reports nominal NARloy-Z zirconium '
                              'content around 0.4-0.5 wt%; the exact material '
                              'specification or heat must be retained for '
                              'design-critical use.'],
              'economic_record': {'status': 'PUBLIC_REFERENCE_PRICE_NOT_AVAILABLE',
                                  'unit_price_per_kg': None,
                                  'currency': None,
                                  'supplier': None,
                                  'material_form': 'Specialty aerospace copper alloy',
                                  'price_source': 'NASA_NARLOY_Z',
                                  'price_date': '2026-08-20',
                                  'source_quality': 'NO_CURRENT_PUBLIC_NUMERIC_PRICE',
                                  'price_basis': 'No defensible public numeric £/kg '
                                                 'reference was qualified.',
                                  'comparison_group': None,
                                  'tax_basis': None,
                                  'reference_price_derivation': None,
                                  'reference_only': True,
                                  'not_cost_input': True}},
 'GRCop-84': {'reference_type': 'METALLIC_ALLOY',
              'material_form': 'NASA Cu-Cr-Nb high-heat-flux alloy',
              'composition': {'Cu': 'Balance', 'Cr': '8 at%', 'Nb': '4 at%'},
              'sources': ['NASA_GRCOP84'],
              'limitations': ['Composition basis is atomic percent, not weight '
                              'percent.'],
              'economic_record': {'status': 'PUBLIC_REFERENCE_PRICE_NOT_AVAILABLE',
                                  'unit_price_per_kg': None,
                                  'currency': None,
                                  'supplier': None,
                                  'material_form': 'Specialty aerospace copper alloy',
                                  'price_source': 'NASA_GRCOP84',
                                  'price_date': '2026-08-20',
                                  'source_quality': 'NO_CURRENT_PUBLIC_NUMERIC_PRICE',
                                  'price_basis': 'No defensible public numeric £/kg '
                                                 'reference was qualified.',
                                  'comparison_group': None,
                                  'tax_basis': None,
                                  'reference_price_derivation': None,
                                  'reference_only': True,
                                  'not_cost_input': True}},
 'GlidCop AL-15': {'reference_type': 'METALLIC_ALLOY',
                   'material_form': 'Dispersion-strengthened copper alloy',
                   'composition': {'Cu': 'Balance', 'Al present as Al2O3': '0.15 wt%'},
                   'sources': ['HOGANAS_GLIDCOP_AL15_2025'],
                   'limitations': ['Composition follows the current Höganäs GLIDCOP '
                                   'AL-15 product datasheet.'],
                   'economic_record': {'status': 'SUPPLIER_QUOTE_REQUIRED',
                                       'unit_price_per_kg': None,
                                       'currency': None,
                                       'supplier': 'Höganäs',
                                       'material_form': 'GLIDCOP AL-15',
                                       'price_source': 'HOGANAS_GLIDCOP_AL15_2025',
                                       'price_date': '2026-08-20',
                                       'source_quality': 'PRIMARY_MANUFACTURER_CONTACT_PRICE',
                                       'price_basis': 'Manufacturer directs customers '
                                                      'to sales/contact; no qualified '
                                                      'public numeric £/kg value.',
                                       'comparison_group': None,
                                       'tax_basis': None,
                                       'reference_price_derivation': None,
                                       'reference_only': True,
                                       'not_cost_input': True}},
 'CuCrZr': {'reference_type': 'METALLIC_ALLOY',
            'material_form': 'UNS C18150 Cu-Cr-Zr alloy',
            'composition': {'Cu': 'Remainder',
                            'Cr': '0.50-1.50 wt%',
                            'Zr': '0.02-0.20 wt%',
                            'Cu + named elements': '>=99.7 wt%'},
            'sources': ['COPPER_ORG_C18150_2026', 'SD_NONFERROUS_CUCRZR_UK_2026'],
            'limitations': ['LEAF maps generic CuCrZr to UNS C18150 for this reference '
                            'record; alternative CuCrZr specifications may use '
                            'narrower chemistry limits.'],
            'economic_record': {'status': 'SUPPLIER_QUOTE_REQUIRED',
                                'unit_price_per_kg': None,
                                'currency': None,
                                'supplier': 'S&D Non-Ferrous Metals',
                                'material_form': 'CW106C / C18150 sheet, round, '
                                                 'hexagon or flat bar',
                                'price_source': 'SD_NONFERROUS_CUCRZR_UK_2026',
                                'price_date': '2026-08-20',
                                'source_quality': 'CURRENT_UK_SUPPLIER_QUOTE_REFERENCE',
                                'price_basis': 'Current UK supplier lists CuCrZr stock '
                                               'but provides pricing through '
                                               'quotation.',
                                'comparison_group': None,
                                'tax_basis': None,
                                'reference_price_derivation': None,
                                'reference_only': True,
                                'not_cost_input': True}},
 'OFHC Copper': {'reference_type': 'METALLIC_ALLOY',
                 'material_form': 'UNS C10100 oxygen-free electronic copper',
                 'composition': {'Cu': '>=99.99 wt% excluding Ag',
                                 'O': '<=0.0005 wt%',
                                 'Ag': '<=0.0025 wt%',
                                 'Fe': '<=0.0010 wt%',
                                 'Pb': '<=0.0005 wt%'},
                 'sources': ['COPPER_ORG_C10100_2026'],
                 'limitations': ['LEAF maps OFHC Copper to C10100 '
                                 'Oxygen-Free-Electronic copper for reference '
                                 'purposes.'],
                 'economic_record': {'status': 'PUBLIC_REFERENCE_PRICE_NOT_AVAILABLE',
                                     'unit_price_per_kg': None,
                                     'currency': None,
                                     'supplier': None,
                                     'material_form': 'C10100 OFE copper',
                                     'price_source': 'COPPER_ORG_C10100_2026',
                                     'price_date': '2026-08-20',
                                     'source_quality': 'NO_CURRENT_PUBLIC_NUMERIC_PRICE',
                                     'price_basis': 'No defensible public numeric £/kg '
                                                    'reference was qualified.',
                                     'comparison_group': None,
                                     'tax_basis': None,
                                     'reference_price_derivation': None,
                                     'reference_only': True,
                                     'not_cost_input': True}},
 'Inconel 718': {'reference_type': 'METALLIC_ALLOY',
                 'material_form': 'INCONEL alloy 718',
                 'composition': {'Ni + Co': '50-55 wt%',
                                 'Cr': '17-21 wt%',
                                 'Fe': 'Balance / nominal approximately 18.5 wt%',
                                 'Nb': 'nominal approximately 5 wt%',
                                 'Mo': 'nominal approximately 3 wt%',
                                 'Ti': 'nominal approximately 1 wt%'},
                 'sources': ['SPECIAL_METALS_718_2026'],
                 'limitations': ['The reference combines Special Metals limiting and '
                                 'nominal chemistry; purchase specifications govern '
                                 'exact allowable limits.'],
                 'economic_record': {'status': 'PUBLIC_REFERENCE_PRICE_NOT_AVAILABLE',
                                     'unit_price_per_kg': None,
                                     'currency': None,
                                     'supplier': 'Special Metals Corporation',
                                     'material_form': 'INCONEL alloy 718',
                                     'price_source': 'SPECIAL_METALS_718_2026',
                                     'price_date': '2026-08-20',
                                     'source_quality': 'NO_CURRENT_PUBLIC_NUMERIC_PRICE',
                                     'price_basis': 'No defensible public numeric £/kg '
                                                    'reference was qualified.',
                                     'comparison_group': None,
                                     'tax_basis': None,
                                     'reference_price_derivation': None,
                                     'reference_only': True,
                                     'not_cost_input': True}},
 'Inconel 625': {'reference_type': 'METALLIC_ALLOY',
                 'material_form': 'INCONEL alloy 625',
                 'composition': {'Ni': 'nominal 61.0 wt%',
                                 'Cr': 'nominal 21.5 wt%',
                                 'Mo': 'nominal 9.0 wt%',
                                 'Nb': 'nominal 3.6 wt%',
                                 'Fe': 'nominal 2.5 wt%'},
                 'sources': ['SPECIAL_METALS_625_2026',
                             'SIGMA_GOODFELLOW_INCONEL625_GB_2026'],
                 'limitations': ['Values are nominal manufacturer chemistry, not '
                                 'procurement limits.'],
                 'economic_record': {'status': 'PUBLIC_RETAIL_REFERENCE',
                                     'unit_price_per_kg': 1687.32,
                                     'currency': 'GBP',
                                     'supplier': 'Sigma-Aldrich UK / Goodfellow',
                                     'material_form': '1000 mm × 6.35 mm diameter '
                                                      'annealed rod',
                                     'price_source': 'SIGMA_GOODFELLOW_INCONEL625_GB_2026',
                                     'price_date': '2026-08-20',
                                     'source_quality': 'CURRENT_PUBLIC_LAB_RETAIL_REFERENCE',
                                     'price_basis': 'Public listed product price '
                                                    '451.00 GBP; reference mass '
                                                    '0.267288 kg derived from the '
                                                    'listed cylindrical dimensions and '
                                                    'LEAF canonical material density '
                                                    '8440 kg/m3.',
                                     'comparison_group': 'LAB_RETAIL_ROD_1000MM_X_6_35MM_GBP',
                                     'tax_basis': 'NOT_STATED_BY_SOURCE',
                                     'reference_price_derivation': '451.00 GBP / '
                                                                   '0.267288 kg = '
                                                                   '1687.32 GBP/kg.',
                                     'reference_only': True,
                                     'not_cost_input': True}},
 'Haynes 230': {'reference_type': 'METALLIC_ALLOY',
                'material_form': 'HAYNES 230 nickel-base alloy',
                'composition': {'Ni': 'Balance / nominal 57 wt%',
                                'Cr': '22 wt%',
                                'W': '14 wt%',
                                'Mo': '2 wt%',
                                'Fe': '<=3 wt%',
                                'Co': '<=5 wt%',
                                'Mn': '0.5 wt%',
                                'Si': '0.4 wt%',
                                'Al': '0.3 wt%',
                                'C': '0.10 wt%',
                                'La': '0.02 wt%',
                                'B': '<=0.015 wt%'},
                'sources': ['HAYNES_230_2025'],
                'limitations': ['Composition is manufacturer nominal chemistry.'],
                'economic_record': {'status': 'PUBLIC_REFERENCE_PRICE_NOT_AVAILABLE',
                                    'unit_price_per_kg': None,
                                    'currency': None,
                                    'supplier': 'Haynes International',
                                    'material_form': 'HAYNES 230 alloy',
                                    'price_source': 'HAYNES_230_2025',
                                    'price_date': '2026-08-20',
                                    'source_quality': 'NO_CURRENT_PUBLIC_NUMERIC_PRICE',
                                    'price_basis': 'No defensible public numeric £/kg '
                                                   'reference was qualified.',
                                    'comparison_group': None,
                                    'tax_basis': None,
                                    'reference_price_derivation': None,
                                    'reference_only': True,
                                    'not_cost_input': True}},
 'Hastelloy X': {'reference_type': 'METALLIC_ALLOY',
                 'material_form': 'HASTELLOY X nickel-base alloy',
                 'composition': {'Ni': 'Balance / nominal 47 wt%',
                                 'Cr': '22 wt%',
                                 'Fe': '18 wt%',
                                 'Mo': '9 wt%',
                                 'Co': '1.5 wt%',
                                 'W': '0.6 wt%',
                                 'C': '0.1 wt%',
                                 'Mn': '<=1 wt%',
                                 'Si': '<=1 wt%'},
                 'sources': ['HAYNES_X_2024', 'SIGMA_GOODFELLOW_HASTELLOYX_US_2026'],
                 'limitations': ['Composition is manufacturer nominal chemistry.'],
                 'economic_record': {'status': 'PUBLIC_RETAIL_REFERENCE',
                                     'unit_price_per_kg': 4994.41,
                                     'currency': 'USD',
                                     'supplier': 'Sigma-Aldrich / Goodfellow',
                                     'material_form': '200 mm × 9.5 mm diameter rod',
                                     'price_source': 'SIGMA_GOODFELLOW_HASTELLOYX_US_2026',
                                     'price_date': '2026-08-20',
                                     'source_quality': 'CURRENT_PUBLIC_LAB_RETAIL_REFERENCE',
                                     'price_basis': 'Public listed product price '
                                                    '582.00 USD; reference mass '
                                                    '0.116530 kg derived from the '
                                                    'listed cylindrical dimensions and '
                                                    'LEAF canonical material density '
                                                    '8220 kg/m3.',
                                     'comparison_group': 'LAB_RETAIL_ROD_200MM_X_9_5MM_USD',
                                     'tax_basis': 'NOT_STATED_BY_SOURCE',
                                     'reference_price_derivation': '582.00 USD / '
                                                                   '0.116530 kg = '
                                                                   '4994.41 USD/kg.',
                                     'reference_only': True,
                                     'not_cost_input': True}},
 '304 Stainless Steel': {'reference_type': 'METALLIC_ALLOY',
                         'material_form': 'AISI 304 stainless steel',
                         'composition': {'Fe': 'Balance',
                                         'C': 'typical 0.04 wt%',
                                         'Cr': 'typical 18.1 wt%',
                                         'Ni': 'typical 8.1 wt%'},
                         'sources': ['OUTOKUMPU_STAINLESS_GRADES',
                                     'RAPTOR_304_FOIL_2026'],
                         'limitations': ['Reference price is a small-quantity UK '
                                         'retail foil reference, not a bulk commodity '
                                         'or manufacturing price.'],
                         'economic_record': {'status': 'PUBLIC_RETAIL_REFERENCE',
                                             'unit_price_per_kg': 82.42,
                                             'currency': 'GBP',
                                             'supplier': 'Raptor Supplies UK',
                                             'material_form': '0.002 in × 12 in × 10 '
                                                              'ft foil roll',
                                             'price_source': 'RAPTOR_304_FOIL_2026',
                                             'price_date': '2026-08-20',
                                             'source_quality': 'CURRENT_PUBLIC_RETAIL_DERIVED_REFERENCE',
                                             'price_basis': '£31.12 inc. VAT retail '
                                                            'item price; mass derived '
                                                            'from listed dimensions '
                                                            'and 8.0 g/cm3 reference '
                                                            'density.',
                                             'comparison_group': 'UK_RETAIL_0.002IN_12IN_10FT_FOIL_INC_VAT',
                                             'tax_basis': 'INC_VAT',
                                             'reference_price_derivation': 'Derived '
                                                                           'reference '
                                                                           '~= '
                                                                           '£82.42/kg. '
                                                                           'Retail/sample-scale '
                                                                           'basis '
                                                                           'only.',
                                             'reference_only': True,
                                             'not_cost_input': True}},
 '316 Stainless Steel': {'reference_type': 'METALLIC_ALLOY',
                         'material_form': 'AISI 316 stainless steel',
                         'composition': {'Fe': 'Balance',
                                         'C': 'typical 0.04 wt%',
                                         'Cr': 'typical 17.2 wt%',
                                         'Ni': 'typical 10.1 wt%',
                                         'Mo': 'typical 2.1 wt%'},
                         'sources': ['OUTOKUMPU_STAINLESS_GRADES',
                                     'RAPTOR_316_BLANK_2026'],
                         'limitations': ['Reference price is for one precision-ground '
                                         'retail blank and must not be treated as a '
                                         'universal 316 price.'],
                         'economic_record': {'status': 'PUBLIC_RETAIL_REFERENCE',
                                             'unit_price_per_kg': 93.34,
                                             'currency': 'GBP',
                                             'supplier': 'Raptor Supplies UK',
                                             'material_form': '1 in × 4 in × 12 in '
                                                              'precision blank',
                                             'price_source': 'RAPTOR_316_BLANK_2026',
                                             'price_date': '2026-08-20',
                                             'source_quality': 'CURRENT_PUBLIC_RETAIL_DERIVED_REFERENCE',
                                             'price_basis': '£585.94 inc. VAT / listed '
                                                            '6.2775 kg product weight.',
                                             'comparison_group': 'UK_RETAIL_PRECISION_BLANK_INC_VAT',
                                             'tax_basis': 'INC_VAT',
                                             'reference_price_derivation': '£585.94 / '
                                                                           '6.2775 kg '
                                                                           '~= '
                                                                           '£93.34/kg.',
                                             'reference_only': True,
                                             'not_cost_input': True}},
 '321 Stainless Steel': {'reference_type': 'METALLIC_ALLOY',
                         'material_form': 'AISI 321 stainless steel',
                         'composition': {'Fe': 'Balance',
                                         'C': 'typical 0.04 wt%',
                                         'Cr': 'typical 17.3 wt%',
                                         'Ni': 'typical 9.1 wt%',
                                         'Ti': 'stabilising addition'},
                         'sources': ['OUTOKUMPU_STAINLESS_GRADES',
                                     'RAPTOR_321_FOIL_2026'],
                         'limitations': ['Reference price is a small-quantity UK '
                                         'retail foil reference, not a bulk commodity '
                                         'or manufacturing price.'],
                         'economic_record': {'status': 'PUBLIC_RETAIL_REFERENCE',
                                             'unit_price_per_kg': 141.83,
                                             'currency': 'GBP',
                                             'supplier': 'Raptor Supplies UK',
                                             'material_form': '0.002 in × 12 in × 10 '
                                                              'ft foil roll',
                                             'price_source': 'RAPTOR_321_FOIL_2026',
                                             'price_date': '2026-08-20',
                                             'source_quality': 'CURRENT_PUBLIC_RETAIL_DERIVED_REFERENCE',
                                             'price_basis': '£52.88 inc. VAT retail '
                                                            'item price; mass derived '
                                                            'from listed dimensions '
                                                            'and 7.9 g/cm3 reference '
                                                            'density.',
                                             'comparison_group': 'UK_RETAIL_0.002IN_12IN_10FT_FOIL_INC_VAT',
                                             'tax_basis': 'INC_VAT',
                                             'reference_price_derivation': 'Derived '
                                                                           'reference '
                                                                           '~= '
                                                                           '£141.83/kg. '
                                                                           'Retail/sample-scale '
                                                                           'basis '
                                                                           'only.',
                                             'reference_only': True,
                                             'not_cost_input': True}},
 '17-4PH Stainless Steel': {'reference_type': 'METALLIC_ALLOY',
                            'material_form': 'UNS S17400 / 17-4PH',
                            'composition': {'Fe': 'Balance',
                                            'Cr': '15.00-17.50 wt%',
                                            'Ni': '3.00-5.00 wt%',
                                            'Cu': '3.00-5.00 wt%',
                                            'Nb + Ta': '0.15-0.45 wt%',
                                            'C': '<=0.07 wt%',
                                            'Mn': '<=1.00 wt%',
                                            'Si': '<=1.00 wt%'},
                            'sources': ['CARPENTER_17_4PH',
                                        'SIGMA_GOODFELLOW_17_4PH_EU_2026'],
                            'limitations': ["Composition follows Carpenter's S17400 "
                                            'product analysis.'],
                            'economic_record': {'status': 'PUBLIC_RETAIL_REFERENCE',
                                                'unit_price_per_kg': 311.17,
                                                'currency': 'EUR',
                                                'supplier': 'Sigma-Aldrich / '
                                                            'Goodfellow',
                                                'material_form': '1000 mm × 16 mm '
                                                                 'diameter rod',
                                                'price_source': 'SIGMA_GOODFELLOW_17_4PH_EU_2026',
                                                'price_date': '2026-08-20',
                                                'source_quality': 'CURRENT_PUBLIC_LAB_RETAIL_REFERENCE',
                                                'price_basis': 'Public listed product '
                                                               'price 488.00 EUR; '
                                                               'reference mass '
                                                               '1.568283 kg derived '
                                                               'from the listed '
                                                               'cylindrical dimensions '
                                                               'and LEAF canonical '
                                                               'material density 7800 '
                                                               'kg/m3.',
                                                'comparison_group': 'LAB_RETAIL_ROD_1000MM_X_16MM_EUR',
                                                'tax_basis': 'NOT_STATED_BY_SOURCE',
                                                'reference_price_derivation': '488.00 '
                                                                              'EUR / '
                                                                              '1.568283 '
                                                                              'kg = '
                                                                              '311.17 '
                                                                              'EUR/kg.',
                                                'reference_only': True,
                                                'not_cost_input': True}}}


COATING_REFERENCE_METADATA = {'YSZ Thermal Barrier Coating': {'composition': {'ZrO2': 'Balance',
                                                 'Y2O3': '8 wt% nominal'},
                                 'sources': ['OERLIKON_METCO_204NS'],
                                 'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET',
                                 'limitations': ['Composition is represented by the '
                                                 'qualified Metco 204NS 8YSZ '
                                                 'reference. The existing LEAF coating '
                                                 'engineering-property record remains '
                                                 'placeholder-mode.']},
 'Alumina Ceramic Coating': {'composition': {'Al2O3': '>=99.9 wt% reference grade'},
                             'sources': ['OERLIKON_METCO_6103'],
                             'source_quality': 'PRIMARY_MANUFACTURER_DATASHEET',
                             'limitations': ['Composition reference uses Metco 6103 '
                                             'high-purity alumina. The existing LEAF '
                                             'coating engineering properties remain '
                                             'placeholder-mode.']},
 'Hafnia Thermal Barrier Coating': {'composition': {'HfO2': 'Hafnium dioxide chemical '
                                                            'identity'},
                                    'sources': ['NIST_HAFNIUM_DIOXIDE'],
                                    'source_quality': 'PRIMARY_REFERENCE_DATABASE',
                                    'limitations': ['The existing generic Hafnia '
                                                    'coating record does not specify '
                                                    'stabilizer, purity, feedstock or '
                                                    'process. HfO2 therefore '
                                                    'identifies the base chemistry '
                                                    'only.']},
 'Rhenium Refractory Liner': {'composition': {'Re': 'Elemental rhenium'},
                              'sources': ['NIST_RHENIUM'],
                              'source_quality': 'PRIMARY_REFERENCE_DATABASE',
                              'limitations': ['This composition identifies elemental '
                                              'rhenium only. The existing LEAF '
                                              'liner/coating engineering-property '
                                              'record remains placeholder-mode.']}}

_FORMULA_TOKEN = re.compile(
    r"([A-Z][a-z]?)(\d*)"
)


def atomic_composition_from_formula(
    formula: str | None,
) -> dict[str, int] | None:

    if not formula:
        return None

    position = 0
    composition: dict[str, int] = {}

    for match in (
        _FORMULA_TOKEN.finditer(
            formula
        )
    ):
        if match.start() != position:
            raise ValueError(
                f"Unsupported chemical formula: {formula!r}"
            )

        element = match.group(
            1
        )

        count_text = match.group(
            2
        )

        count = (
            int(count_text)
            if count_text
            else 1
        )

        composition[
            element
        ] = (
            composition.get(
                element,
                0,
            )
            +
            count
        )

        position = match.end()

    if (
        position != len(formula)
        or
        not composition
    ):
        raise ValueError(
            f"Unsupported chemical formula: {formula!r}"
        )

    return composition


def _source_records(
    keys,
):
    return [
        {
            "source_id":
                key,

            **deepcopy(
                SOURCE_REGISTRY[
                    key
                ]
            ),
        }

        for key in keys

        if key in SOURCE_REGISTRY
    ]


def _chemistry_record(
    parent_identity,
):
    metadata = deepcopy(
        PURE_SUBSTANCE_METADATA[
            parent_identity
        ]
    )

    source_key = metadata.pop(
        "source"
    )

    formula = metadata[
        "chemical_formula"
    ]

    metadata[
        "atomic_composition"
    ] = (
        atomic_composition_from_formula(
            formula
        )
    )

    metadata[
        "structure_reference"
    ] = (
        "NIST Chemistry WebBook SRD 69 "
        f"chemical-structure record; CAS "
        f"{metadata['cas_number']}"
    )

    metadata[
        "sources"
    ] = (
        _source_records(
            [
                source_key
            ]
        )
    )

    return metadata


def _economic_record(
    metadata,
):
    record = deepcopy(
        metadata.get(
            "economic_record"
        )
        or
        {}
    )

    if not record:
        return {
            "status":
                "NOT_AVAILABLE",

            "unit_price_per_kg":
                None,

            "currency":
                None,

            "supplier":
                None,

            "material_form":
                metadata.get(
                    "material_form"
                ),

            "price_source":
                None,

            "price_date":
                None,

            "source_quality":
                None,
        }

    value = record.get(
        "unit_price_per_kg"
    )

    if value is not None:
        value = float(
            value
        )

        if value < 0:
            raise ValueError(
                "unit_price_per_kg cannot be negative"
            )

    record[
        "unit_price_per_kg"
    ] = value

    quality = str(
        record.get(
            "source_quality"
        )
        or
        ""
    ).upper()

    if (
        value is not None

        and

        quality
        in
        UNACCEPTABLE_SOURCE_QUALITIES
    ):
        raise ValueError(
            "Economic unit price requires acceptable source quality"
        )

    return record


def _base_record(
    *,
    reference_id,
    category,
    canonical_name,
    display_name,
    aliases,
    reference_type,
):
    if reference_type not in REFERENCE_TYPES:
        raise ValueError(
            f"Unknown reference type: {reference_type}"
        )

    return {
        "reference_id":
            reference_id,

        "category":
            category,

        "canonical_name":
            canonical_name,

        "display_name":
            display_name,

        "aliases":
            list(
                aliases
                or
                []
            ),

        "reference_type":
            reference_type,

        "phase":
            None,

        "parent_identity":
            None,

        "chemical_formula":
            None,

        "atomic_composition":
            None,

        "molecular_weight":
            None,

        "cas_number":
            None,

        "inchi":
            None,

        "structure_reference":
            None,

        "structural_representation":
            None,

        "composition":
            None,

        "engineering_properties":
            {},

        "economic_record":
            {
                "status":
                    "NOT_AVAILABLE",

                "unit_price_per_kg":
                    None,

                "currency":
                    None,

                "supplier":
                    None,

                "material_form":
                    None,

                "price_source":
                    None,

                "price_date":
                    None,

                "source_quality":
                    None,
            },

        "sources":
            [],

        "source_quality":
            None,

        "limitations":
            [],
    }


def _material_record(
    name,
):
    engineering = (
        material_database
        .get_material(
            name
        )
    )

    metadata = deepcopy(
        MATERIAL_REFERENCE_METADATA.get(
            name,
            {}
        )
    )

    reference_type = (
        metadata.get(
            "reference_type"
        )
        or
        "METALLIC_ALLOY"
    )

    record = _base_record(
        reference_id=
            f"MATERIAL::{name}",

        category=
            "Materials",

        canonical_name=
            name,

        display_name=
            name,

        aliases=
            [],

        reference_type=
            reference_type,
    )

    record[
        "engineering_properties"
    ] = deepcopy(
        engineering
    )

    record[
        "composition"
    ] = deepcopy(
        metadata.get(
            "composition"
        )
    )

    record[
        "economic_record"
    ] = _economic_record(
        metadata
    )

    source_ids = list(
        metadata.get(
            "sources"
        )
        or
        []
    )

    record[
        "sources"
    ] = _source_records(
        source_ids
    )

    record[
        "source_quality"
    ] = (
        metadata.get(
            "source_quality"
        )
        or
        engineering.get(
            "source_quality"
        )
    )

    record[
        "limitations"
    ] = list(
        metadata.get(
            "limitations"
        )
        or
        []
    )

    if (
        record[
            "composition"
        ]
        is None
    ):
        record[
            "limitations"
        ].append(
            "No source-qualified elemental composition has yet "
            "been attached to the reference projection."
        )

    return record



def _coating_record(
    name,
):
    engineering = (
        material_database
        .get_coating_material_properties(
            name
        )
    )

    metadata = deepcopy(
        COATING_REFERENCE_METADATA.get(
            name,
            {}
        )
    )

    record = _base_record(
        reference_id=
            f"COATING::{name}",

        category=
            "Coatings",

        canonical_name=
            name,

        display_name=
            name,

        aliases=
            [],

        reference_type=
            "COATING",
    )

    record[
        "engineering_properties"
    ] = deepcopy(
        engineering
    )

    record[
        "composition"
    ] = deepcopy(
        metadata.get(
            "composition"
        )
    )

    record[
        "sources"
    ] = _source_records(
        metadata.get(
            "sources"
        )
        or
        []
    )

    record[
        "source_quality"
    ] = (
        metadata.get(
            "source_quality"
        )
        or
        engineering.get(
            "source_quality"
        )
    )

    record[
        "limitations"
    ] = list(
        metadata.get(
            "limitations"
        )
        or
        []
    )

    citation = engineering.get(
        "citation"
    )

    if citation:
        record[
            "sources"
        ].append({
            "source_id":
                "EXISTING_COATING_CITATION",

            "authority":
                None,

            "reference":
                citation,

            "source_quality":
                engineering.get(
                    "source_quality"
                ),
        })

    if engineering.get(
        "source_is_placeholder"
    ):
        record[
            "limitations"
        ].append(
            "Current coating engineering-property data are "
            "explicitly placeholder-mode and cannot generate "
            "an engineering PASS."
        )

    record[
        "economic_record"
    ] = {
        "status":
            "PUBLIC_REFERENCE_PRICE_NOT_AVAILABLE",

        "unit_price_per_kg":
            None,

        "currency":
            None,

        "supplier":
            None,

        "material_form":
            "Thermal / refractory coating reference",

        "price_source":
            None,

        "price_date":
            "2026-08-20",

        "source_quality":
            "NO_CURRENT_PUBLIC_NUMERIC_PRICE",

        "price_basis":
            "No qualified public numeric £/kg reference "
            "has yet been attached.",

        "comparison_group":
            None,

        "tax_basis":
            None,

        "reference_price_derivation":
            None,

        "reference_only":
            True,

        "not_cost_input":
            True,
    }

    return record


def _propellant_record(
    *,
    category,
    canonical_name,
    source_record,
):
    metadata = deepcopy(
        PROPELLANT_REFERENCE_METADATA.get(
            canonical_name,
            {}
        )
    )

    reference_type = metadata.get(
        "reference_type"
    )

    if not reference_type:
        raise KeyError(
            "Missing reference metadata for "
            f"{canonical_name!r}"
        )

    record = _base_record(
        reference_id=
            f"{category.upper()}::{canonical_name}",

        category=
            category,

        canonical_name=
            canonical_name,

        display_name=
            source_record.get(
                "display_name"
            )
            or
            canonical_name,

        aliases=
            source_record.get(
                "aliases"
            )
            or
            [],

        reference_type=
            reference_type,
    )

    record[
        "phase"
    ] = metadata.get(
        "phase"
    )

    parent_identity = metadata.get(
        "parent_identity"
    )

    record[
        "parent_identity"
    ] = parent_identity

    if parent_identity:
        chemistry = (
            _chemistry_record(
                parent_identity
            )
        )

        for key in (
            "chemical_formula",
            "atomic_composition",
            "molecular_weight",
            "cas_number",
            "inchi",
            "structure_reference",
            "structural_representation",
        ):
            record[
                key
            ] = chemistry[
                key
            ]

        record[
            "sources"
        ].extend(
            chemistry[
                "sources"
            ]
        )

    record[
        "composition"
    ] = deepcopy(
        metadata.get(
            "composition"
        )
    )

    record[
        "sources"
    ].extend(
        _source_records(
            metadata.get(
                "sources"
            )
            or
            []
        )
    )

    record[
        "limitations"
    ] = list(
        metadata.get(
            "limitations"
        )
        or
        []
    )

    engineering = deepcopy(
        source_record
    )

    record[
        "engineering_properties"
    ] = engineering

    if record[
        "sources"
    ]:
        record[
            "source_quality"
        ] = (
            record[
                "sources"
            ][
                0
            ].get(
                "source_quality"
            )
        )

    if reference_type == "MIXTURE":
        for key in (
            "chemical_formula",
            "atomic_composition",
            "molecular_weight",
            "cas_number",
            "inchi",
            "structure_reference",
            "structural_representation",
        ):
            record[
                key
            ] = None

    return record


def build_engineering_reference_catalog():
    materials = {
        name:
            _material_record(
                name
            )

        for name in (
            material_database
            .get_material_names()
        )
    }

    coatings = {
        name:
            _coating_record(
                name
            )

        for name in (
            material_database
            .get_coating_material_names()
        )
    }

    fuels = {
        name:
            _propellant_record(
                category=
                    "Fuels",

                canonical_name=
                    name,

                source_record=
                    propellant_database
                    .FUEL_DATABASE[
                        name
                    ],
            )

        for name in (
            propellant_database
            .get_all_fuel_options()
        )
    }

    oxidizers = {
        name:
            _propellant_record(
                category=
                    "Oxidisers",

                canonical_name=
                    name,

                source_record=
                    propellant_database
                    .OXIDIZER_DATABASE[
                        name
                    ],
            )

        for name in (
            propellant_database
            .get_all_oxidizer_options()
        )
    }

    return {
        "Materials":
            materials,

        "Coatings":
            coatings,

        "Fuels":
            fuels,

        "Oxidisers":
            oxidizers,
    }


def get_reference_record(
    category,
    canonical_name,
):
    catalog = (
        build_engineering_reference_catalog()
    )

    return deepcopy(
        catalog[
            category
        ][
            canonical_name
        ]
    )


def flatten_reference_catalog():
    catalog = (
        build_engineering_reference_catalog()
    )

    return [
        deepcopy(
            record
        )

        for category_records in (
            catalog.values()
        )

        for record in (
            category_records.values()
        )
    ]
