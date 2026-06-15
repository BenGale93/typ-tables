# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
