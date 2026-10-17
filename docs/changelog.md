# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Fixed

* Integer column selectors now resolve against the source data columns, so the
  internal `__row_index` column no longer shifts positions. `columns=0` selects
  the first source column, negative indices still select from the end, and every
  method agrees with `cols_move`.
* `sub_missing` now only substitutes the exact `"nan"` token in string columns
  instead of any value containing `"nan"` as a substring (e.g. `"financial"` or
  `"banana"`). Formatted `NaN` values are still replaced.
* Column-label styles are now resolved against the source data, so dtype-based
  selectors (for example `ncs.numeric()`) keep matching columns after a formatter
  such as `fmt_number` has converted them to strings.
* `fmt_currency(use_subunits=False)` now drops the subunits and rounds to whole
  currency units instead of being silently ignored.
* `fmt_date`/`fmt_datetime` with `date_style="year_quarter"` now render the
  quarter (for example `2026-Q4`) instead of a literal `%q`.
* `fmt_number(decimals=0, drop_trailing_zeros=True)` no longer strips zeros from
  the integer part, so `100` renders as `100` rather than `1` and `1000` as
  `1,000` rather than `1,`.
* Escaping of formatted values is now robust: values containing unbalanced
  `<typst>`/`</typst>` markers no longer raise `ValueError`, and multiple
  formatted regions in a single value are all preserved instead of only the
  first.
* `cols_align` no longer emits the row-group warning when aligning other columns.
  The warning now only fires when the row-group column is selected explicitly,
  and the default selection skips it.
* Row selectors now accept negative indices (`-1` selects the last row, matching
  column selection) and raise a clear `IndexError` for out-of-range indices
  instead of silently doing nothing.

## 0.3.1 - 2026-06-16

### Fixed

* `clear_defaults` now clears all default styles.

## 0.3.0 - 2026-06-15

### Added

* `with_id` for labelling tables for referencing purposes.
* `column_labels_hidden` in the `tab_options` method. For hiding the header.
* `tab_spanner_delim` for programmatically creating spanners from column names.

## 0.2.0 - 2026-05-30

### Added

* `tab_spanner` method for adding grouped column headers.
* `LocSpanner` for targeting spanners for styling.
* `cols_move` method for moving table columns after another column.
* Pipe method for applying functions to `TypTable` objects in a method chain.
* `tab_footer` method for adding table footer notes.
* `LocFooter` for targeting the footer for styling.

### Changed

* Changed rendering pipeline to centralise string concatenation.

## 0.1.4 - 2026-05-10

### Fix

* Fix not being able to use expression to style columns that had been formatted.

### Documented

* Comparison between pure Typst and `typ-tables`.
