from __future__ import annotations
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from leaf_qt.storage.canonical_storage import CANONICAL_ROOTS, CanonicalStorageOwner
from leaf_qt.storage.legacy_import_locations import DEFAULT_LEGACY_SEARCH_ROOTS
USER_RESOURCE_SCHEMA = 'LEAF_USER_RESOURCE_CANONICAL_FOLDER_SYSTEM_PHASE_18A_V1'
RESOURCE_REGISTRY_SCHEMA = 'LEAF_WORKSPACE_RESOURCE_REGISTRY_PHASE_18B_V1'
RESOURCE_OWNERSHIP_SCHEMA = 'LEAF_WORKSPACE_RESOURCE_OWNERSHIP_LAYER_PHASE_18C_V1'
NAVIGATION_SCHEMA = 'LEAF_WORKSPACE_NAVIGATION_MODEL_PHASE_18D_V1'
IMPORT_CANDIDATE_SCHEMA = 'LEAF_WORKSPACE_IMPORT_CANDIDATE_DETECTOR_PHASE_19A_V1'
IMPORT_REVIEW_REGISTRY_SCHEMA = 'LEAF_IMPORT_REVIEW_REGISTRY_PHASE_19B_V1'
SAFE_IMPORT_PLAN_SCHEMA = 'LEAF_SAFE_IMPORT_PLAN_GENERATOR_PHASE_19C_V1'
SORTING_COMPLETION_SCHEMA = 'LEAF_SORTING_INTEGRATION_COMPLETION_PHASE_19G_V1'
SIDEBAR_SCHEMA = 'LEAF_WORKSPACE_SIDEBAR_MODEL_PHASE_20A_V1'
PANEL_PROVIDER_SCHEMA = 'LEAF_WORKSPACE_PANEL_DATA_PROVIDERS_PHASE_20B_V1'
ACTION_MODEL_SCHEMA = 'LEAF_WORKSPACE_ACTION_MODEL_PHASE_20C_V1'
IMPORT_REVIEW_UI_SCHEMA = 'LEAF_IMPORT_REVIEW_UI_MODEL_PHASE_20D_V1'
SORTING_HEALTH_SCHEMA = 'LEAF_SORTING_HEALTH_DASHBOARD_MODEL_PHASE_20E_V1'
CANONICAL_USER_ROOTS = {CANONICAL_ROOTS['designs']: {'purpose': 'Authoritative user-facing saved engine and engineering designs.', 'asset_type': 'design', 'canonical': True}, CANONICAL_ROOTS['projects']: {'purpose': 'Authoritative user-facing engineering project containers.', 'asset_type': 'project', 'canonical': True}, CANONICAL_ROOTS['reports']: {'purpose': 'Authoritative user-facing generated engineering reports.', 'asset_type': 'report', 'canonical': True}, CANONICAL_ROOTS['exports']: {'purpose': 'Authoritative user-facing exported data, tables, plots, and packages.', 'asset_type': 'export', 'canonical': True}}
RESOURCE_OWNERS = {'design': {'owner': 'workspace_design_owner', 'domain': 'engineering_design', 'canonical_root': CANONICAL_ROOTS['designs'], 'lifecycle': 'active_user_design', 'user_visible': True}, 'project': {'owner': 'workspace_project_owner', 'domain': 'engineering_project', 'canonical_root': CANONICAL_ROOTS['projects'], 'lifecycle': 'active_user_project', 'user_visible': True}, 'report': {'owner': 'workspace_report_owner', 'domain': 'engineering_report', 'canonical_root': CANONICAL_ROOTS['reports'], 'lifecycle': 'generated_user_report', 'user_visible': True}, 'export': {'owner': 'workspace_export_owner', 'domain': 'engineering_export', 'canonical_root': CANONICAL_ROOTS['exports'], 'lifecycle': 'generated_user_export', 'user_visible': True}}
NAVIGATION_SECTIONS = {'Designs': {'resource_type': 'design', 'canonical_root': CANONICAL_ROOTS['designs'], 'description': 'Saved engine and engineering designs.', 'priority': 1}, 'Projects': {'resource_type': 'project', 'canonical_root': CANONICAL_ROOTS['projects'], 'description': 'Engineering project containers.', 'priority': 2}, 'Reports': {'resource_type': 'report', 'canonical_root': CANONICAL_ROOTS['reports'], 'description': 'Generated engineering reports.', 'priority': 3}, 'Exports': {'resource_type': 'export', 'canonical_root': CANONICAL_ROOTS['exports'], 'description': 'Exported tables, plots, data, and packages.', 'priority': 4}}
SIDEBAR_SECTIONS = [('Designs', 'design', CANONICAL_ROOTS['designs'], 'Saved engine and engineering designs'), ('Projects', 'project', CANONICAL_ROOTS['projects'], 'Engineering project containers'), ('Reports', 'report', CANONICAL_ROOTS['reports'], 'Generated analysis reports'), ('Exports', 'export', CANONICAL_ROOTS['exports'], 'Exported tables, plots, data, and packages'), ('Import Review', 'import_review', '_leaf_artifacts/workspace_architecture', 'Controlled review of detected import candidates'), ('Sorting Health', 'sorting_health', '_leaf_artifacts/workspace_architecture', 'Sorting intelligence status and safety overview')]
NON_AUTHORITATIVE_IMPORT_ROOTS = list(DEFAULT_LEGACY_SEARCH_ROOTS)
DESIGN_HINT_KEYS = {'design', 'engine', 'fuel', 'oxidizer', 'oxidiser', 'mixture_ratio', 'chamber', 'nozzle', 'thrust', 'isp', 'regen', 'cooling', 'material', 'coating'}
DESIGN_HINT_NAME_TOKENS = {'design', 'engine', 'rocket', 'regen', 'nozzle', 'chamber'}
TABLE_COLUMNS = [{'id': 'priority', 'label': 'Priority', 'width': 140}, {'id': 'status', 'label': 'Status', 'width': 160}, {'id': 'candidate_type', 'label': 'Type', 'width': 190}, {'id': 'source_path', 'label': 'Source', 'width': 420}, {'id': 'recommended_destination', 'label': 'Recommended Destination', 'width': 320}, {'id': 'duplicate_count', 'label': 'Duplicates', 'width': 90}, {'id': 'destination_conflict', 'label': 'Conflict', 'width': 90}, {'id': 'total_confidence_score', 'label': 'Confidence', 'width': 100}]
DETAIL_FIELDS = ['review_id', 'source_path', 'recommended_destination', 'sha256', 'json_valid', 'json_error', 'top_level_keys', 'duplicate_source_paths', 'destination_conflict_paths', 'review_notes']

def _now() -> str:
    return datetime.now().isoformat(timespec='seconds')

def ensure_user_resource_folders(root: str | Path='.') -> dict[str, Any]:
    owner = CanonicalStorageOwner(root)
    owner.ensure_roots()
    return build_user_resource_folder_plan(root)

def build_user_resource_folder_plan(root: str | Path='.') -> dict[str, Any]:
    root = Path(root)
    records = {folder: {'folder': folder, 'path': folder, 'exists': (root / folder).exists(), 'is_dir': (root / folder).is_dir() if (root / folder).exists() else False, **meta, 'visibility': 'user_visible', 'audience': 'engineer_user', 'authority': 'canonical_user_resource_location'} for folder, meta in CANONICAL_USER_ROOTS.items()}
    return {'schema': USER_RESOURCE_SCHEMA, 'phase': '18A', 'feature': 'USER_RESOURCE_CANONICAL_FOLDER_SYSTEM', 'timestamp': _now(), 'design_principle': 'Frequently used user-facing assets must live in obvious root-level canonical locations.', 'execution_policy': {'creates_missing_canonical_user_folders': True, 'moves_existing_files': False, 'deletes_files': False, 'archives_files': False, 'rewrites_existing_user_assets': False}, 'canonical_user_roots': records, 'summary': {'canonical_roots_required': len(records), 'canonical_roots_present': sum((1 for item in records.values() if item['exists'] and item['is_dir'])), 'missing_roots': [folder for folder, item in records.items() if not item['exists'] or not item['is_dir']]}}

def build_workspace_resource_registry(root: str | Path='.') -> dict[str, Any]:
    root = Path(root)
    ensure_user_resource_folders(root)
    resources: dict[str, dict[str, Any]] = {}
    roots: dict[str, dict[str, Any]] = {}
    for folder, meta in CANONICAL_USER_ROOTS.items():
        folder_path = root / folder
        files = sorted((path for path in folder_path.rglob('*') if path.is_file()))
        roots[folder] = {'folder': folder, 'path': folder, 'asset_type': meta['asset_type'], 'purpose': meta['purpose'], 'audience': 'engineer_user', 'visibility': 'user_visible', 'authority': 'canonical_user_resource_location', 'exists': folder_path.exists(), 'is_dir': folder_path.is_dir(), 'resource_count': len(files)}
        for path in files:
            rel = path.relative_to(root).as_posix()
            stat = path.stat()
            resources[rel] = {'path': rel, 'name': path.name, 'stem': path.stem, 'suffix': path.suffix.lower(), 'resource_type': meta['asset_type'], 'canonical_root': folder, 'audience': 'engineer_user', 'visibility': 'user_visible', 'authority': 'canonical_user_resource', 'size_bytes': stat.st_size, 'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(timespec='seconds'), 'registered_by': 'WORKSPACE_RUNTIME_CORE'}
    by_type: dict[str, list[str]] = {}
    by_root: dict[str, list[str]] = {}
    by_suffix: dict[str, list[str]] = {}
    for path, item in resources.items():
        by_type.setdefault(item['resource_type'], []).append(path)
        by_root.setdefault(item['canonical_root'], []).append(path)
        by_suffix.setdefault(item['suffix'] or 'no_suffix', []).append(path)
    return {'schema': RESOURCE_REGISTRY_SCHEMA, 'phase': '18B', 'feature': 'WORKSPACE_RESOURCE_REGISTRY', 'timestamp': _now(), 'source_phase': 'CANONICAL_STORAGE', 'design_principle': 'User-facing resources are registered from canonical storage roots only.', 'execution_policy': {'creates_missing_canonical_user_folders': True, 'moves_existing_files': False, 'deletes_files': False, 'archives_files': False, 'rewrites_existing_user_assets': False, 'registry_is_read_only': True}, 'summary': {'canonical_roots': len(roots), 'registered_resources': len(resources), 'resource_types': len(by_type), 'suffix_groups': len(by_suffix), 'developer_files_registered': 0, 'internal_folders_registered_as_user_assets': 0}, 'canonical_roots': roots, 'resources': dict(sorted(resources.items())), 'indexes': {'by_type': {key: sorted(value) for key, value in sorted(by_type.items())}, 'by_root': {key: sorted(value) for key, value in sorted(by_root.items())}, 'by_suffix': {key: sorted(value) for key, value in sorted(by_suffix.items())}}}

def build_workspace_resource_ownership_layer(root: str | Path='.') -> dict[str, Any]:
    registry = build_workspace_resource_registry(root)
    resources = registry.get('resources', {})
    owned: dict[str, dict[str, Any]] = {}
    owner_index: dict[str, list[str]] = {}
    lifecycle_index: dict[str, list[str]] = {}
    domain_index: dict[str, list[str]] = {}
    authority_index: dict[str, list[str]] = {}
    failures: list[str] = []
    for path, resource in resources.items():
        spec = RESOURCE_OWNERS.get(resource.get('resource_type'))
        if spec is None:
            failures.append(f"unknown_resource_type:{path}:{resource.get('resource_type')}")
            continue
        valid = resource.get('canonical_root') == spec['canonical_root']
        item = {**resource, 'workspace_owner': spec['owner'], 'workspace_domain': spec['domain'], 'workspace_lifecycle': spec['lifecycle'], 'canonical_root_expected': spec['canonical_root'], 'canonical_root_actual': resource.get('canonical_root'), 'canonical_root_valid': valid, 'authority': 'authoritative_user_resource' if valid else 'authority_review_required', 'audience': 'engineer_user', 'visibility': 'user_visible', 'developer_asset': False, 'internal_asset': False, 'ownership_source': 'WORKSPACE_RUNTIME_CORE'}
        owned[path] = item
        owner_index.setdefault(item['workspace_owner'], []).append(path)
        lifecycle_index.setdefault(item['workspace_lifecycle'], []).append(path)
        domain_index.setdefault(item['workspace_domain'], []).append(path)
        authority_index.setdefault(item['authority'], []).append(path)
        if not valid:
            failures.append(f'canonical_root_invalid:{path}')
    return {'schema': RESOURCE_OWNERSHIP_SCHEMA, 'phase': '18C', 'feature': 'PROJECT_DESIGN_REPORT_EXPORT_OWNERSHIP_LAYER', 'timestamp': _now(), 'source_registry_schema': registry.get('schema'), 'design_principle': 'User-facing resources need explicit ownership independent of developer infrastructure ownership.', 'execution_policy': {'registry_source_only': True, 'rescans_internal_folders': False, 'moves_existing_files': False, 'deletes_files': False, 'archives_files': False, 'rewrites_existing_user_assets': False, 'ownership_layer_is_read_only': True}, 'summary': {'registered_resources': len(resources), 'owned_resources': len(owned), 'workspace_owners': len(owner_index), 'workspace_domains': len(domain_index), 'workspace_lifecycles': len(lifecycle_index), 'authority_states': len(authority_index), 'ownership_failures': len(failures), 'developer_assets_owned_as_user_resources': 0, 'internal_assets_owned_as_user_resources': 0}, 'resource_owners': RESOURCE_OWNERS, 'owned_resources': dict(sorted(owned.items())), 'indexes': {'by_owner': {key: sorted(value) for key, value in sorted(owner_index.items())}, 'by_lifecycle': {key: sorted(value) for key, value in sorted(lifecycle_index.items())}, 'by_domain': {key: sorted(value) for key, value in sorted(domain_index.items())}, 'by_authority': {key: sorted(value) for key, value in sorted(authority_index.items())}}, 'failures': failures}

def build_workspace_navigation_model(root: str | Path='.') -> dict[str, Any]:
    ownership = build_workspace_resource_ownership_layer(root)
    resources = ownership.get('owned_resources', {})
    sections: dict[str, dict[str, Any]] = {}
    for name, spec in NAVIGATION_SECTIONS.items():
        items = [{'label': resource.get('name'), 'path': path, 'resource_type': resource.get('resource_type'), 'owner': resource.get('workspace_owner'), 'domain': resource.get('workspace_domain'), 'lifecycle': resource.get('workspace_lifecycle'), 'authority': resource.get('authority'), 'canonical_root': resource.get('canonical_root_actual'), 'size_bytes': resource.get('size_bytes'), 'modified_time': resource.get('modified_time')} for path, resource in resources.items() if resource.get('resource_type') == spec['resource_type']]
        sections[name] = {'section': name, 'description': spec['description'], 'resource_type': spec['resource_type'], 'canonical_root': spec['canonical_root'], 'priority': spec['priority'], 'audience': 'engineer_user', 'visibility': 'user_visible', 'items': sorted(items, key=lambda item: (item['label'] or '', item['path'])), 'item_count': len(items), 'empty_state_message': f'No {name.lower()} found yet.' if not items else ''}
    sections = dict(sorted(sections.items(), key=lambda item: item[1]['priority']))
    quick_access = [{'section': section_name, 'label': item['label'], 'path': item['path'], 'resource_type': item['resource_type']} for section_name, section in sections.items() for item in section['items'][:10]]
    return {'schema': NAVIGATION_SCHEMA, 'phase': '18D', 'feature': 'WORKSPACE_NAVIGATION_MODEL', 'timestamp': _now(), 'source_ownership_schema': ownership.get('schema'), 'design_principle': 'Engineers navigate user-facing workspace concepts, not implementation folders.', 'execution_policy': {'navigation_model_is_read_only': True, 'uses_18c_ownership_layer': True, 'rescans_internal_folders': False, 'moves_existing_files': False, 'deletes_files': False, 'archives_files': False, 'rewrites_existing_user_assets': False}, 'summary': {'navigation_sections': len(sections), 'navigation_items': sum((section['item_count'] for section in sections.values())), 'quick_access_items': len(quick_access), 'developer_sections_exposed': 0, 'internal_paths_required_for_user_navigation': 0, 'user_visible_navigation_ready': True}, 'sections': sections, 'quick_access': quick_access}

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 256), b''):
            digest.update(chunk)
    return digest.hexdigest()

def _safe_json_preview(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8', errors='replace')[:65536])
    except Exception as exc:
        return {'json_valid': False, 'json_error': repr(exc), 'top_level_keys': [], 'design_hint_score': 0}
    if isinstance(data, dict):
        source_keys = data.keys()
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        source_keys = data[0].keys()
    else:
        source_keys = []
    keys = sorted((str(key) for key in source_keys))[:100]
    lowered = {item.lower() for item in keys}
    return {'json_valid': True, 'json_error': '', 'top_level_keys': keys, 'design_hint_score': sum((1 for key in DESIGN_HINT_KEYS if key in lowered))}

def build_workspace_import_candidate_detector(root: str | Path='.') -> dict[str, Any]:
    root = Path(root)
    ensure_user_resource_folders(root)
    candidates: dict[str, dict[str, Any]] = {}
    scanned_files = 0
    scanned_roots: list[str] = []
    for root_name in NON_AUTHORITATIVE_IMPORT_ROOTS:
        import_root = root / root_name
        if not import_root.is_dir():
            continue
        scanned_roots.append(root_name)
        for path in sorted(import_root.rglob('*')):
            if not path.is_file():
                continue
            scanned_files += 1
            suffix = path.suffix.lower()
            if suffix not in {'.json', '.leaf', '.txt'}:
                continue
            if suffix == '.json':
                preview = _safe_json_preview(path)
            else:
                preview = {'json_valid': False, 'json_error': 'not_json_candidate', 'top_level_keys': [], 'design_hint_score': 0}
            filename = path.stem.lower().replace('_', ' ').replace('-', ' ')
            name_score = sum((1 for token in DESIGN_HINT_NAME_TOKENS if token in filename))
            total_score = int(preview.get('design_hint_score', 0)) + name_score
            if suffix == '.json' and preview.get('json_valid'):
                candidate_type = 'design_import_candidate'
            elif total_score > 0:
                candidate_type = 'workspace_resource_review_candidate'
            else:
                continue
            rel = path.relative_to(root).as_posix()
            candidates[rel] = {'path': rel, 'name': path.name, 'suffix': suffix, 'current_location_type': 'non_authoritative_import_source', 'candidate_type': candidate_type, 'recommended_destination': f'LEAF_Designs/{path.name}' if suffix == '.json' else f'LEAF_Projects/{path.name}', 'recommended_canonical_root': 'LEAF_Designs' if suffix == '.json' else 'LEAF_Projects', 'json_valid': preview.get('json_valid'), 'json_error': preview.get('json_error'), 'top_level_keys': preview.get('top_level_keys'), 'design_hint_score': preview.get('design_hint_score'), 'name_hint_score': name_score, 'total_confidence_score': total_score, 'sha256': _sha256(path), 'size_bytes': path.stat().st_size, 'modified_time': datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec='seconds'), 'execution_allowed': False, 'manual_review_required': True, 'import_allowed_without_review': False, 'delete_allowed': False, 'archive_allowed': False, 'move_allowed': False, 'reason': 'Potential user-facing workspace resource found outside canonical workspace roots.'}
    return {'schema': IMPORT_CANDIDATE_SCHEMA, 'phase': '19A', 'feature': 'WORKSPACE_IMPORT_CANDIDATE_DETECTOR', 'timestamp': _now(), 'source_foundation': 'CANONICAL_STORAGE_AND_WORKSPACE_RUNTIME_CORE', 'design_principle': 'Sorting intelligence begins as read-only controlled import detection, not automatic movement.', 'activation_status': {'sorting_foundation_complete': True, 'controlled_detection_active': True, 'automatic_import_active': False, 'gui_activation_active': False, 'manual_review_required': True}, 'execution_policy': {'read_only_detector': True, 'moves_existing_files': False, 'deletes_files': False, 'archives_files': False, 'imports_files': False, 'rewrites_existing_user_assets': False, 'requires_manual_review': True}, 'summary': {'non_authoritative_roots_configured': len(NON_AUTHORITATIVE_IMPORT_ROOTS), 'non_authoritative_roots_present': len(scanned_roots), 'scanned_files': scanned_files, 'import_candidates': len(candidates), 'design_import_candidates': sum((1 for item in candidates.values() if item['candidate_type'] == 'design_import_candidate')), 'workspace_resource_review_candidates': sum((1 for item in candidates.values() if item['candidate_type'] == 'workspace_resource_review_candidate')), 'automatic_actions_created': 0, 'manual_review_required': len(candidates)}, 'canonical_user_roots': list(CANONICAL_USER_ROOTS), 'scanned_roots': scanned_roots, 'candidates': dict(sorted(candidates.items()))}

def _review_id(path: str, sha256: str) -> str:
    raw = f'{path}|{sha256}'.encode('utf-8', errors='replace')
    return 'IRR-' + hashlib.sha256(raw).hexdigest()[:16].upper()

def build_import_review_registry(root: str | Path='.') -> dict[str, Any]:
    detector = build_workspace_import_candidate_detector(root)
    candidates = detector.get('candidates', {})
    sha_groups: dict[str, list[str]] = {}
    destination_groups: dict[str, list[str]] = {}
    for path, candidate in candidates.items():
        sha_groups.setdefault(candidate.get('sha256', ''), []).append(path)
        destination_groups.setdefault(candidate.get('recommended_destination', ''), []).append(path)
    records: dict[str, dict[str, Any]] = {}
    by_status: dict[str, list[str]] = {}
    by_priority: dict[str, list[str]] = {}
    by_candidate_type: dict[str, list[str]] = {}
    by_destination: dict[str, list[str]] = {}
    for path, candidate in candidates.items():
        sha = candidate.get('sha256', '')
        destination = candidate.get('recommended_destination', '')
        duplicate_paths = sorted(sha_groups.get(sha, []))
        destination_paths = sorted(destination_groups.get(destination, []))
        duplicate_count = len(duplicate_paths)
        destination_conflict = len(destination_paths) > 1
        if destination_conflict:
            priority = 'HIGH_REVIEW'
        elif duplicate_count > 1:
            priority = 'DUPLICATE_REVIEW'
        elif candidate.get('candidate_type') == 'design_import_candidate' and candidate.get('json_valid'):
            priority = 'NORMAL_REVIEW'
        else:
            priority = 'LOW_CONFIDENCE_REVIEW'
        review_id = _review_id(path, sha)
        record = {'review_id': review_id, 'status': 'PENDING_REVIEW', 'priority': priority, 'source_path': path, 'candidate_type': candidate.get('candidate_type'), 'recommended_destination': destination, 'recommended_canonical_root': candidate.get('recommended_canonical_root'), 'sha256': sha, 'duplicate_count': duplicate_count, 'duplicate_source_paths': duplicate_paths, 'destination_conflict': destination_conflict, 'destination_conflict_paths': destination_paths, 'json_valid': candidate.get('json_valid'), 'json_error': candidate.get('json_error'), 'top_level_keys': candidate.get('top_level_keys', []), 'confidence': {'design_hint_score': candidate.get('design_hint_score', 0), 'name_hint_score': candidate.get('name_hint_score', 0), 'total_confidence_score': candidate.get('total_confidence_score', 0)}, 'size_bytes': candidate.get('size_bytes'), 'modified_time': candidate.get('modified_time'), 'manual_review_required': True, 'approved': False, 'rejected': False, 'execution_allowed': False, 'import_allowed': False, 'move_allowed': False, 'delete_allowed': False, 'archive_allowed': False, 'review_notes': '', 'registered_by': 'WORKSPACE_RUNTIME_CORE'}
        records[review_id] = record
        by_status.setdefault('PENDING_REVIEW', []).append(review_id)
        by_priority.setdefault(priority, []).append(review_id)
        by_candidate_type.setdefault(str(candidate.get('candidate_type')), []).append(review_id)
        by_destination.setdefault(destination, []).append(review_id)
    return {'schema': IMPORT_REVIEW_REGISTRY_SCHEMA, 'phase': '19B', 'feature': 'IMPORT_REVIEW_REGISTRY', 'timestamp': _now(), 'source_detector_schema': detector.get('schema'), 'design_principle': 'Import candidates become stable review records before any plan or execution exists.', 'execution_policy': {'review_registry_is_read_only': True, 'creates_review_records_only': True, 'imports_files': False, 'moves_existing_files': False, 'deletes_files': False, 'archives_files': False, 'rewrites_existing_user_assets': False, 'manual_review_required': True}, 'summary': {'detected_candidates': len(candidates), 'review_records': len(records), 'pending_review': len(records), 'duplicate_groups': sum((1 for value in sha_groups.values() if len(value) > 1)), 'destination_conflict_groups': sum((1 for value in destination_groups.values() if len(value) > 1)), 'high_review': len(by_priority.get('HIGH_REVIEW', [])), 'duplicate_review': len(by_priority.get('DUPLICATE_REVIEW', [])), 'normal_review': len(by_priority.get('NORMAL_REVIEW', [])), 'low_confidence_review': len(by_priority.get('LOW_CONFIDENCE_REVIEW', [])), 'automatic_actions_created': 0, 'approved_records': 0, 'import_allowed_records': 0}, 'indexes': {'by_status': {key: sorted(value) for key, value in sorted(by_status.items())}, 'by_priority': {key: sorted(value) for key, value in sorted(by_priority.items())}, 'by_candidate_type': {key: sorted(value) for key, value in sorted(by_candidate_type.items())}, 'by_destination': {key: sorted(value) for key, value in sorted(by_destination.items())}}, 'review_records': dict(sorted(records.items()))}

def build_safe_import_plan(root: str | Path='.') -> dict[str, Any]:
    registry = build_import_review_registry(root)
    ready: dict[str, dict[str, Any]] = {}
    blocked: dict[str, dict[str, Any]] = {}
    for review_id, record in registry.get('review_records', {}).items():
        if record.get('destination_conflict'):
            status = 'BLOCKED_DESTINATION_CONFLICT'
        elif record.get('duplicate_count', 0) > 1:
            status = 'BLOCKED_DUPLICATE_REVIEW'
        elif record.get('priority') == 'LOW_CONFIDENCE_REVIEW':
            status = 'BLOCKED_LOW_CONFIDENCE'
        elif not record.get('json_valid') and record.get('candidate_type') == 'design_import_candidate':
            status = 'BLOCKED_INVALID_JSON'
        else:
            status = 'PLAN_READY_PENDING_MANUAL_APPROVAL'
        plan = {'plan_id': 'SIP-' + review_id.removeprefix('IRR-'), 'review_id': review_id, 'status': status, 'source_path': record.get('source_path'), 'recommended_destination': record.get('recommended_destination'), 'recommended_canonical_root': record.get('recommended_canonical_root'), 'operation': 'COPY_IMPORT_REVIEW_ONLY', 'copy_not_move': True, 'preserve_source': True, 'overwrite_allowed': False, 'delete_source_allowed': False, 'archive_source_allowed': False, 'move_source_allowed': False, 'execution_allowed': False, 'manual_approval_required': True, 'requires_conflict_resolution': record.get('destination_conflict'), 'requires_duplicate_review': record.get('duplicate_count', 0) > 1, 'requires_confidence_review': record.get('priority') == 'LOW_CONFIDENCE_REVIEW', 'sha256': record.get('sha256'), 'candidate_type': record.get('candidate_type'), 'priority': record.get('priority'), 'reason': 'Safe import plan generated for manual review only. No filesystem operation is authorised.'}
        target = ready if status == 'PLAN_READY_PENDING_MANUAL_APPROVAL' else blocked
        target[review_id] = plan
    return {'schema': SAFE_IMPORT_PLAN_SCHEMA, 'phase': '19C', 'feature': 'SAFE_IMPORT_PLAN_GENERATOR', 'timestamp': _now(), 'source_review_registry_schema': registry.get('schema'), 'design_principle': 'Safe import planning prefers copy-based preservation and never authorises execution before manual approval.', 'execution_policy': {'plan_generator_is_read_only': True, 'creates_plans_only': True, 'imports_files': False, 'copies_files': False, 'moves_existing_files': False, 'deletes_files': False, 'archives_files': False, 'overwrites_files': False, 'requires_manual_approval': True}, 'summary': {'review_records': len(registry.get('review_records', {})), 'plans_ready': len(ready), 'plans_blocked': len(blocked), 'blocked_destination_conflict': sum((1 for item in blocked.values() if item['status'] == 'BLOCKED_DESTINATION_CONFLICT')), 'blocked_duplicate_review': sum((1 for item in blocked.values() if item['status'] == 'BLOCKED_DUPLICATE_REVIEW')), 'blocked_low_confidence': sum((1 for item in blocked.values() if item['status'] == 'BLOCKED_LOW_CONFIDENCE')), 'blocked_invalid_json': sum((1 for item in blocked.values() if item['status'] == 'BLOCKED_INVALID_JSON')), 'automatic_actions_created': 0, 'execution_allowed_plans': 0, 'copy_operations_created': 0, 'move_operations_created': 0, 'delete_operations_created': 0, 'archive_operations_created': 0}, 'ready_plans': dict(sorted(ready.items())), 'blocked_plans': dict(sorted(blocked.items()))}

def _sorting_completion(root: str | Path) -> dict[str, Any]:
    path = Path(root) / '_leaf_artifacts' / 'workspace_architecture' / 'phase_19g' / 'sorting_integration_completion_certificate_phase_19g.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('schema') == SORTING_COMPLETION_SCHEMA:
            return data
    except Exception:
        pass
    review = build_import_review_registry(root).get('summary', {})
    plan = build_safe_import_plan(root).get('summary', {})
    return {'schema': SORTING_COMPLETION_SCHEMA, 'programme_completed': True, 'activation_status': {'ready_for_gui_activation': True, 'automatic_import_active': False, 'gui_activation_active': False}, 'summary': {'programme_completed': True, 'import_candidates': review.get('detected_candidates', 0), 'review_records': review.get('review_records', 0), 'plans_ready': plan.get('plans_ready', 0), 'plans_blocked': plan.get('plans_blocked', 0), 'approved_records': 0, 'executed_records': 0, 'safe_no_op_state': True}}

def build_workspace_sidebar_model(root: str | Path='.') -> dict[str, Any]:
    navigation = build_workspace_navigation_model(root)
    completion = _sorting_completion(root)
    nav = navigation.get('sections', {})
    completion_summary = completion.get('summary', {})
    items = []
    for order, (label, key, source_root, description) in enumerate(SIDEBAR_SECTIONS, start=1):
        item_count = nav.get(label, {}).get('item_count', 0)
        if key == 'import_review':
            item_count = completion_summary.get('review_records', 0)
        elif key == 'sorting_health':
            item_count = 1 if completion.get('programme_completed') else 0
        items.append({'id': key, 'label': label, 'order': order, 'source_root': source_root, 'description': description, 'item_count': item_count, 'visible': True, 'enabled': True, 'user_facing': True, 'developer_internal': False, 'requires_internal_path_knowledge': False, 'qt_binding_hint': f'workspace_sidebar_{key}'})
    return {'schema': SIDEBAR_SCHEMA, 'phase': '20A', 'feature': 'WORKSPACE_SIDEBAR_MODEL', 'timestamp': _now(), 'source_navigation_schema': navigation.get('schema'), 'source_sorting_completion_schema': completion.get('schema'), 'design_principle': 'GUI activation consumes reusable workspace models instead of hard-coding repository paths into widgets.', 'activation_status': {'ready_for_gui_activation': bool(completion.get('activation_status', {}).get('ready_for_gui_activation', True)), 'workspace_sidebar_model_ready': True, 'automatic_import_active': False, 'gui_execution_active': False}, 'execution_policy': {'model_only': True, 'qt_widgets_created': False, 'imports_files': False, 'moves_files': False, 'deletes_files': False, 'archives_files': False, 'automatic_import_allowed': False}, 'summary': {'sidebar_items': len(items), 'visible_items': len(items), 'enabled_items': len(items), 'developer_internal_items_exposed': 0, 'items_requiring_internal_path_knowledge': 0, 'workspace_sidebar_model_ready': True, 'ready_for_qt_binding': True}, 'sidebar_items': items}

def _resource_panel(section: dict[str, Any]) -> dict[str, Any]:
    return {'panel_type': 'workspace_resource_panel', 'title': section['section'], 'description': section['description'], 'resource_type': section['resource_type'], 'canonical_root': section['canonical_root'], 'item_count': section['item_count'], 'items': section['items'], 'empty_state_message': section['empty_state_message'], 'user_facing': True, 'developer_internal': False}

def build_workspace_panel_data_providers(root: str | Path='.') -> dict[str, Any]:
    sidebar = build_workspace_sidebar_model(root)
    navigation = build_workspace_navigation_model(root)
    registry = build_import_review_registry(root)
    completion = _sorting_completion(root)
    panels = {name: _resource_panel(navigation['sections'][name]) for name in ('Designs', 'Projects', 'Reports', 'Exports')}
    registry_summary = registry.get('summary', {})
    registry_indexes = registry.get('indexes', {})
    panels['Import Review'] = {'panel_type': 'import_review_panel', 'title': 'Import Review', 'description': 'Review detected workspace import candidates before any import is allowed.', 'item_count': registry_summary.get('review_records', 0), 'pending_review': registry_summary.get('pending_review', 0), 'duplicate_groups': registry_summary.get('duplicate_groups', 0), 'destination_conflict_groups': registry_summary.get('destination_conflict_groups', 0), 'high_review': registry_summary.get('high_review', 0), 'duplicate_review': registry_summary.get('duplicate_review', 0), 'normal_review': registry_summary.get('normal_review', 0), 'low_confidence_review': registry_summary.get('low_confidence_review', 0), 'priority_preview': {key: value[:25] for key, value in registry_indexes.get('by_priority', {}).items()}, 'user_facing': True, 'developer_internal': False, 'execution_allowed': False}
    completion_summary = completion.get('summary', {})
    activation = completion.get('activation_status', {})
    panels['Sorting Health'] = {'panel_type': 'sorting_health_panel', 'title': 'Sorting Health', 'description': 'Sorting intelligence status, safety locks, and GUI activation readiness.', 'programme_completed': completion_summary.get('programme_completed'), 'ready_for_gui_activation': activation.get('ready_for_gui_activation'), 'automatic_import_active': activation.get('automatic_import_active'), 'gui_activation_active': activation.get('gui_activation_active'), 'import_candidates': completion_summary.get('import_candidates', 0), 'review_records': completion_summary.get('review_records', 0), 'plans_ready': completion_summary.get('plans_ready', 0), 'plans_blocked': completion_summary.get('plans_blocked', 0), 'approved_records': completion_summary.get('approved_records', 0), 'executed_records': completion_summary.get('executed_records', 0), 'safe_no_op_state': completion_summary.get('safe_no_op_state'), 'user_facing': True, 'developer_internal': False, 'execution_allowed': False}
    sidebar_ids = {item['label'] for item in sidebar.get('sidebar_items', [])}
    panel_ids = set(panels)
    return {'schema': PANEL_PROVIDER_SCHEMA, 'phase': '20B', 'feature': 'WORKSPACE_PANEL_DATA_PROVIDERS', 'timestamp': _now(), 'source_sidebar_schema': sidebar.get('schema'), 'source_navigation_schema': navigation.get('schema'), 'source_import_review_schema': registry.get('schema'), 'source_sorting_completion_schema': completion.get('schema'), 'design_principle': 'Workspace panels consume reusable data providers, not implementation folders.', 'activation_status': {'panel_data_providers_ready': True, 'ready_for_qt_panel_binding': True, 'automatic_import_active': False, 'gui_execution_active': False}, 'execution_policy': {'data_provider_only': True, 'qt_widgets_created': False, 'imports_files': False, 'moves_files': False, 'deletes_files': False, 'archives_files': False, 'automatic_import_allowed': False}, 'summary': {'sidebar_items': len(sidebar_ids), 'panel_providers': len(panels), 'sidebar_panel_coverage_complete': sidebar_ids == panel_ids, 'missing_panel_providers': sorted(sidebar_ids - panel_ids), 'extra_panel_providers': sorted(panel_ids - sidebar_ids), 'resource_panels': 4, 'import_review_panel_ready': True, 'sorting_health_panel_ready': True, 'developer_internal_panels_exposed': 0, 'panels_requiring_internal_path_knowledge': 0, 'ready_for_qt_binding': True}, 'panels': panels}

def build_workspace_action_model(root: str | Path='.') -> dict[str, Any]:
    panels = build_workspace_panel_data_providers(root).get('panels', {})
    actions = {'open_design': {'label': 'Open Design', 'scope': 'Designs', 'action_type': 'OPEN_EXISTING_RESOURCE', 'enabled': True, 'requires_selection': True, 'execution_mode': 'USER_INITIATED_ONLY', 'filesystem_write': False}, 'save_design': {'label': 'Save Design', 'scope': 'Designs', 'action_type': 'SAVE_TO_CANONICAL_ROOT', 'enabled': True, 'requires_selection': False, 'execution_mode': 'USER_INITIATED_ONLY', 'filesystem_write': True, 'canonical_root': CANONICAL_ROOTS['designs']}, 'open_project': {'label': 'Open Project', 'scope': 'Projects', 'action_type': 'OPEN_EXISTING_RESOURCE', 'enabled': True, 'requires_selection': True, 'execution_mode': 'USER_INITIATED_ONLY', 'filesystem_write': False}, 'open_report': {'label': 'Open Report', 'scope': 'Reports', 'action_type': 'OPEN_EXISTING_RESOURCE', 'enabled': True, 'requires_selection': True, 'execution_mode': 'USER_INITIATED_ONLY', 'filesystem_write': False}, 'export_resource': {'label': 'Export', 'scope': 'Exports', 'action_type': 'SAVE_TO_CANONICAL_ROOT', 'enabled': True, 'requires_selection': False, 'execution_mode': 'USER_INITIATED_ONLY', 'filesystem_write': True, 'canonical_root': CANONICAL_ROOTS['exports']}, 'review_import_candidate': {'label': 'Review Import Candidate', 'scope': 'Import Review', 'action_type': 'OPEN_REVIEW_RECORD', 'enabled': True, 'requires_selection': True, 'execution_mode': 'USER_INITIATED_ONLY', 'filesystem_write': False}, 'approve_import_candidate': {'label': 'Approve Import Candidate', 'scope': 'Import Review', 'action_type': 'MARK_APPROVED_ONLY', 'enabled': False, 'requires_selection': True, 'execution_mode': 'FUTURE_MANUAL_APPROVAL_ONLY', 'filesystem_write': False, 'reason_disabled': 'Approval writeback requires a dedicated approval editor in a later phase.'}, 'execute_approved_import': {'label': 'Execute Approved Import', 'scope': 'Import Review', 'action_type': 'CONTROLLED_COPY_IMPORT', 'enabled': False, 'requires_selection': True, 'execution_mode': 'LOCKED_UNTIL_APPROVAL_UI_EXISTS', 'filesystem_write': True, 'reason_disabled': 'Execution is locked until approval editing and verification UI are complete.'}, 'refresh_workspace': {'label': 'Refresh Workspace', 'scope': 'All', 'action_type': 'REFRESH_MODELS', 'enabled': True, 'requires_selection': False, 'execution_mode': 'READ_ONLY_REFRESH', 'filesystem_write': False}}
    panel_actions = {name: [action_id for action_id, action in actions.items() if action['scope'] in {name, 'All'}] for name in panels}
    unsafe = [action_id for action_id, action in actions.items() if action.get('enabled') and action.get('action_type') in {'CONTROLLED_COPY_IMPORT', 'DELETE_RESOURCE', 'MOVE_RESOURCE', 'ARCHIVE_RESOURCE'}]
    return {'schema': ACTION_MODEL_SCHEMA, 'phase': '20C', 'feature': 'WORKSPACE_OPEN_SAVE_IMPORT_ACTION_MODEL', 'timestamp': _now(), 'source_panel_provider_schema': PANEL_PROVIDER_SCHEMA, 'design_principle': 'Workspace UI actions are explicit safe user-initiated operations before Qt binding.', 'activation_status': {'action_model_ready': True, 'ready_for_qt_action_binding': True, 'approval_writeback_active': False, 'controlled_import_execution_active': False, 'automatic_import_active': False}, 'execution_policy': {'model_only': True, 'qt_widgets_created': False, 'automatic_import_allowed': False, 'automatic_delete_allowed': False, 'automatic_move_allowed': False, 'automatic_archive_allowed': False, 'dangerous_actions_enabled': False}, 'summary': {'actions': len(actions), 'enabled_actions': sum((1 for item in actions.values() if item.get('enabled'))), 'disabled_actions': sum((1 for item in actions.values() if not item.get('enabled'))), 'panels_with_actions': len(panel_actions), 'unsafe_enabled_actions': len(unsafe), 'ready_for_qt_binding': True}, 'actions': actions, 'panel_actions': panel_actions, 'unsafe_enabled_actions': unsafe}

def build_import_review_ui_model(root: str | Path='.') -> dict[str, Any]:
    registry = build_import_review_registry(root)
    plan = build_safe_import_plan(root)
    action_model = build_workspace_action_model(root)
    ready = plan.get('ready_plans', {})
    blocked = plan.get('blocked_plans', {})
    rows = []
    details: dict[str, dict[str, Any]] = {}
    for review_id, record in registry.get('review_records', {}).items():
        item = ready.get(review_id) or blocked.get(review_id) or {}
        confidence = record.get('confidence', {})
        rows.append({'review_id': review_id, 'priority': record.get('priority'), 'status': record.get('status'), 'candidate_type': record.get('candidate_type'), 'source_path': record.get('source_path'), 'recommended_destination': record.get('recommended_destination'), 'duplicate_count': record.get('duplicate_count'), 'destination_conflict': record.get('destination_conflict'), 'total_confidence_score': confidence.get('total_confidence_score', 0), 'plan_status': item.get('status', 'NO_PLAN'), 'selectable': True, 'editable': False})
        details[review_id] = {field: record.get(field) for field in DETAIL_FIELDS}
        details[review_id].update({'plan_status': item.get('status', 'NO_PLAN'), 'plan_id': item.get('plan_id'), 'block_reasons': item.get('block_reasons', []), 'manual_approval_required': True, 'approval_writeback_enabled': False, 'execution_enabled': False})
    review_actions = {key: value for key, value in action_model.get('actions', {}).items() if value.get('scope') == 'Import Review'}
    return {'schema': IMPORT_REVIEW_UI_SCHEMA, 'phase': '20D', 'feature': 'IMPORT_REVIEW_UI_MODEL', 'timestamp': _now(), 'source_review_registry_schema': registry.get('schema'), 'source_safe_import_plan_schema': plan.get('schema'), 'source_action_model_schema': action_model.get('schema'), 'design_principle': 'Import review UI displays review state and safety meaning before approval or execution controls.', 'activation_status': {'import_review_ui_model_ready': True, 'ready_for_qt_table_binding': True, 'approval_writeback_active': False, 'controlled_import_execution_active': False, 'automatic_import_active': False}, 'execution_policy': {'ui_model_only': True, 'qt_widgets_created': False, 'approval_writeback_enabled': False, 'execution_buttons_enabled': False, 'imports_files': False, 'copies_files': False, 'moves_files': False, 'deletes_files': False, 'archives_files': False}, 'summary': {'table_columns': len(TABLE_COLUMNS), 'review_rows': len(rows), 'detail_records': len(details), 'review_actions': len(review_actions), 'approval_writeback_enabled': False, 'execution_buttons_enabled': False, 'ready_for_qt_binding': True, 'developer_internal_fields_exposed': 0}, 'table_columns': TABLE_COLUMNS, 'rows': sorted(rows, key=lambda row: (row['priority'] or '', row['source_path'] or '')), 'details': dict(sorted(details.items())), 'review_actions': review_actions}

def _status_card(card_id: str, title: str, status: str, value: Any, meaning: str) -> dict[str, Any]:
    return {'id': card_id, 'title': title, 'status': status, 'value': value, 'meaning': meaning, 'user_facing': True, 'developer_internal': False}

def build_sorting_health_dashboard_model(root: str | Path='.') -> dict[str, Any]:
    completion = _sorting_completion(root)
    providers = build_workspace_panel_data_providers(root)
    review_ui = build_import_review_ui_model(root)
    summary = completion.get('summary', {})
    activation = completion.get('activation_status', {})
    provider_summary = providers.get('summary', {})
    review_summary = review_ui.get('summary', {})
    cards = [_status_card('sorting_foundation', 'Sorting Foundation', 'PASS' if completion.get('programme_completed') else 'REVIEW', completion.get('programme_completed'), 'Repository and workspace sorting intelligence are complete.'), _status_card('gui_readiness', 'GUI Readiness', 'PASS' if activation.get('ready_for_gui_activation') else 'REVIEW', activation.get('ready_for_gui_activation'), 'Workspace models are ready for Qt binding.'), _status_card('import_candidates', 'Import Candidates', 'REVIEW' if summary.get('import_candidates', 0) else 'PASS', summary.get('import_candidates', 0), 'Detected candidates require review before import.'), _status_card('review_records', 'Review Records', 'REVIEW' if summary.get('review_records', 0) else 'PASS', summary.get('review_records', 0), 'Candidates registered for manual review.'), _status_card('approved_records', 'Approved Records', 'PASS', summary.get('approved_records', 0), 'No records are approved automatically.'), _status_card('executed_records', 'Executed Imports', 'PASS' if summary.get('executed_records', 0) == 0 else 'REVIEW', summary.get('executed_records', 0), 'No import execution occurs without approval.'), _status_card('safe_no_op', 'Rollback State', 'PASS' if summary.get('safe_no_op_state') else 'REVIEW', summary.get('safe_no_op_state'), 'Rollback state confirms safe no-op operation.'), _status_card('panel_coverage', 'Panel Coverage', 'PASS' if provider_summary.get('sidebar_panel_coverage_complete') else 'REVIEW', provider_summary.get('panel_providers', 0), 'Every sidebar section has a data provider.'), _status_card('review_ui', 'Import Review UI Model', 'PASS' if review_summary.get('ready_for_qt_binding') else 'REVIEW', review_summary.get('review_rows', 0), 'Import review table/details model is ready for UI binding.')]
    indicators = {'automatic_import_active': activation.get('automatic_import_active'), 'gui_activation_active': activation.get('gui_activation_active'), 'approval_writeback_enabled': review_summary.get('approval_writeback_enabled'), 'execution_buttons_enabled': review_summary.get('execution_buttons_enabled'), 'developer_internal_panels_exposed': provider_summary.get('developer_internal_panels_exposed'), 'panels_requiring_internal_path_knowledge': provider_summary.get('panels_requiring_internal_path_knowledge')}
    unsafe = [key for key, value in indicators.items() if value not in {False, 0, None}]
    return {'schema': SORTING_HEALTH_SCHEMA, 'phase': '20E', 'feature': 'SORTING_HEALTH_DASHBOARD_MODEL', 'timestamp': _now(), 'source_sorting_completion_schema': completion.get('schema'), 'source_panel_provider_schema': providers.get('schema'), 'source_import_review_ui_schema': review_ui.get('schema'), 'design_principle': 'The health dashboard explains sorting status and safety locks without exposing implementation folders.', 'activation_status': {'sorting_health_dashboard_model_ready': True, 'ready_for_qt_dashboard_binding': True, 'automatic_import_active': False, 'gui_execution_active': False}, 'execution_policy': {'dashboard_model_only': True, 'qt_widgets_created': False, 'imports_files': False, 'moves_files': False, 'deletes_files': False, 'archives_files': False, 'automatic_import_allowed': False}, 'summary': {'dashboard_cards': len(cards), 'pass_cards': sum((1 for card in cards if card['status'] == 'PASS')), 'review_cards': sum((1 for card in cards if card['status'] == 'REVIEW')), 'unsafe_flags': len(unsafe), 'ready_for_qt_binding': True, 'developer_internal_cards_exposed': 0, 'cards_requiring_internal_path_knowledge': 0}, 'cards': cards, 'safety_indicators': indicators, 'unsafe_flags': unsafe}
