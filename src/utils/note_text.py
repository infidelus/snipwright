"""Headlines for the export summary that the dialog can translate.

The exporter and the joiner run in worker threads and write their notes and
errors in English, because the log is what a problem report is read from and
it must read the same whoever sent it.  The completion dialog is a different
matter: a German user should see German there.

A `NoteText` is an ordinary `str` - the English text, so logging, joining and
comparing it all work exactly as before - that also remembers the template
and values it was built from.  The dialog translates the template and fills
the values in again.  A value that is itself a `NoteText` is translated the
same way, which is how "<headline> - see logs" keeps both halves translatable.

Every template must also be marked with `QT_TRANSLATE_NOOP("ExportNotes",
...)` where it is written, or `pyside6-lupdate` never sees it and it stays in
English with nothing to say so.
"""

CONTEXT = "ExportNotes"


class NoteText(str):
    """English text that remembers its template and values."""

    def __new__(cls, template, *args):
        text = str.__new__(cls, template % args if args else template)
        text.template = template
        text.args = args
        return text


def counted(n, one, many):
    """`one` or `many` by `n`, as a NoteText carrying `n`.

    Kept as two whole sentences rather than a pasted-on "s", because German
    plurals do not work that way and a translator needs both forms.
    """
    return NoteText(one if n == 1 else many, n)


def translate_note(text, translate):
    """The dialog's half: `text` in the user's language.

    `translate` is `QCoreApplication.translate`, passed in so this module
    needs no Qt of its own.  Anything that does not survive formatting - a
    translation whose placeholders do not match, say - falls back to the
    English rather than losing the note.
    """
    template = getattr(text, "template", None)
    if template is None:
        return translate(CONTEXT, str(text))
    args = tuple(translate_note(a, translate) if isinstance(a, NoteText)
                 else a for a in text.args)
    try:
        out = translate(CONTEXT, template)
        return out % args if args else out
    except (TypeError, ValueError):
        return str(text)
