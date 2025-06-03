CREATE TABLE vulnerability_info (
    cve_id TEXT PRIMARY KEY,
    affected_library_package_name TEXT,
    vulnerable_versions_found TEXT[], -- Array of strings
    known_fixed_versions TEXT[], -- Array of strings
    initial_affected_code_mentions TEXT[], -- Array of strings
    suggested_patch_details JSONB, -- JSONB to store nested JSON structure
    sources_used TEXT[] -- Array of strings
);

INSERT INTO vulnerability_info (
    cve_id,
    affected_library_package_name,
    vulnerable_versions_found,
    known_fixed_versions,
    initial_affected_code_mentions,
    suggested_patch_details,
    sources_used
) VALUES (
    'CVE-2022-24999',
    'qs',
    ARRAY[
        'before 6.10.3', '6.2.x prior to 6.2.4', '6.3.x prior to 6.3.3',
        '6.4.x prior to 6.4.1', '6.5.x prior to 6.5.3', '6.6.x prior to 6.6.1',
        '6.7.x prior to 6.7.3', '6.8.x prior to 6.8.3', '6.9.x prior to 6.9.7',
        '6.10.x prior to 6.10.3', 'versions up to (excluding) 6.2.4',
        'versions from (including) 6.3.0 up to (excluding) 6.3.3', '6.4.0',
        'versions from (including) 6.5.0 up to (excluding) 6.5.3', '6.6.0',
        'versions from (including) 6.7.0 up to (excluding) 6.7.3',
        'versions from (including) 6.8.0 up to (excluding) 6.8.3',
        'versions from (including) 6.9.0 up to (excluding) 6.9.7',
        'versions from (including) 6.10.0 up to (excluding) 6.10.3'
    ],
    ARRAY[
        '6.10.3', '6.9.7', '6.8.3', '6.7.3', '6.6.1', '6.5.3', '6.4.1',
        '6.3.3', '6.2.4'
    ],
    ARRAY['__proto__ key'],
    '{
        "description": "The vulnerability is due to improper input validation of query strings. The fix involves modifying the way that the web UI processes the URL to prevent prototype pollution.",
        "diff": null,
        "replacement_snippets": [],
        "instructions": "Apply the most recent upgrade or patch from the vendor. Specifically, update to qs version 6.10.3 or later."
    }'::JSONB,
    ARRAY[
        'https://nvd.nist.gov/vuln/detail/CVE-2022-24999', 
        'https://www.mend.io/vulnerability-database/CVE-2022-24999'
    ]
);
