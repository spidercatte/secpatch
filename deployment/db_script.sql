-- Create the vulnerability_info table
CREATE TABLE vulnerability_info (
    cve_id TEXT PRIMARY KEY,
    affected_library_package_name TEXT,
    vulnerable_versions_found TEXT[], -- Array of strings
    known_fixed_versions TEXT[], -- Array of strings
    initial_affected_code_mentions TEXT[], -- Array of strings
    suggested_patch_details JSONB, -- JSONB to store nested JSON structure
    sources_used TEXT[] -- Array of strings
);

-- Insert data into the vulnerability_info table
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
        'before 6.10.3', 
        '6.2.x prior to 6.2.4', 
        '6.3.x prior to 6.3.3',
        '6.4.x prior to 6.4.1', 
        '6.5.x prior to 6.5.3', 
        '6.6.x prior to 6.6.1'
    ],
    NULL, -- Replace with actual known fixed versions if available
    NULL, -- Replace with actual initial affected code mentions if available
    '{"details": "Update to qs version 6.10.3 or later"}'::JSONB,
    ARRAY['https://www.mend.io/vulnerability-database/CVE-2022-24999']
);