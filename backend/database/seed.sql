-- =============================================================================
-- LineByLine — Seed Data (Phase 7C, REVISED 6-table architecture)
--
-- Seeded content: ONLY the concepts canonical reference table.
--
-- DELIBERATELY ABSENT (per simplified architecture):
--   - NO prerequisite graph (static graph not used; Gemini dynamic)
--   - NO resources catalog (static URLs not used; Gemini dynamic; existing
--     explanation_engine/resources.py is the in-code fallback)
--
-- SAFE: All inserts use INSERT ... ON CONFLICT DO NOTHING.
-- =============================================================================

INSERT INTO public.concepts (id, name, slug, description, language) VALUES
  ('00000000-0000-4000-8000-000000000001', 'Variables & Assignment',     'variables',          'Named storage locations and the = operator.',                     'python'),
  ('00000000-0000-4000-8000-000000000002', 'Data Types',                 'data-types',         'Numbers, strings, booleans, None, type conversions.',            'python'),
  ('00000000-0000-4000-8000-000000000003', 'Operators & Expressions',    'operators',          'Arithmetic, comparison, logical, and assignment operators.',     'python'),
  ('00000000-0000-4000-8000-000000000004', 'Conditional Statements',     'conditional-statements', 'if / elif / else and boolean flow.',                       'python'),
  ('00000000-0000-4000-8000-000000000005', 'While Loops',                'while-loops',        'Condition-based iteration with while.',                           'python'),
  ('00000000-0000-4000-8000-000000000006', 'For Loops & Range',          'for-loops',          'Sequence iteration, range(), loop boundaries.',                  'python'),
  ('00000000-0000-4000-8000-000000000007', 'Lists',                      'lists',              'Ordered mutable sequences in Python.',                           'python'),
  ('00000000-0000-4000-8000-000000000008', 'List Indexing',              'list-indexing',      'Zero-based and negative indexing into a list.',                  'python'),
  ('00000000-0000-4000-8000-000000000009', 'List Slicing',               'list-slicing',       'Extracting sublists via [start:stop:step].',                     'python'),
  ('00000000-0000-4000-8000-000000000010', 'Tuples',                     'tuples',             'Immutable sequences and packing/unpacking.',                     'python'),
  ('00000000-0000-4000-8000-000000000011', 'Dictionaries',               'dictionaries',       'Key/value lookup structures.',                                   'python'),
  ('00000000-0000-4000-8000-000000000012', 'Sets',                       'sets',               'Unordered unique collections and set operations.',               'python'),
  ('00000000-0000-4000-8000-000000000013', 'Functions',                  'functions',          'Defining reusable blocks of code with def.',                     'python'),
  ('00000000-0000-4000-8000-000000000014', 'Function Parameters',        'function-parameters','Positional, default, *args, **kwargs parameters.',               'python'),
  ('00000000-0000-4000-8000-000000000015', 'Return Values',              'return-values',      'Returning single, multiple, and None values from functions.',    'python'),
  ('00000000-0000-4000-8000-000000000016', 'Variable Scope & Namespaces','variable-scope',     'Local, enclosing, global, built-in (LEGB rule).',                'python'),
  ('00000000-0000-4000-8000-000000000017', 'Strings',                    'strings',            'String literals, escape sequences, immutability.',              'python'),
  ('00000000-0000-4000-8000-000000000018', 'String Formatting / F-strings','f-strings',         'Formatted output with f-strings and str.format().',             'python'),
  ('00000000-0000-4000-8000-000000000019', 'Exception Handling',         'exception-handling', 'try / except / else / finally, raising errors.',                'python'),
  ('00000000-0000-4000-8000-000000000020', 'List Comprehensions',        'list-comprehensions','Compact [expr for x in iter if cond] syntax.',                   'python'),
  ('00000000-0000-4000-8000-000000000021', 'Mutability',                 'mutability',         'Mutable vs. immutable types in Python.',                         'python'),
  ('00000000-0000-4000-8000-000000000022', 'Sorting',                    'sorting',            'list.sort(), sorted(), key functions.',                          'python'),
  ('00000000-0000-4000-8000-000000000023', 'Recursion',                  'recursion',          'Base case + recursive step for self-referential algorithms.',   'python'),
  ('00000000-0000-4000-8000-000000000024', 'Classes & OOP',              'classes-oop',        'Classes, instances, attributes, __init__, methods.',            'python'),
  ('00000000-0000-4000-8000-000000000025', 'File I/O',                   'file-io',            'Reading and writing files, context managers, with blocks.',     'python'),
  ('00000000-0000-4000-8000-000000000026', 'Algorithms & Complexity',    'algorithms-complexity','Big-O notation + common algorithm patterns.',                  'python')
ON CONFLICT (slug) DO NOTHING;
