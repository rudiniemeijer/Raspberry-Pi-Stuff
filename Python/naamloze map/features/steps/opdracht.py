@given(u'There is an empty text file available to us')
def step_impl(context):
    context.filename = "./opdracht.txt"
    mijn_bestand = open(context.filename, "wt")
    mijn_bestand.close()


@when(u'I open this file')
def step_impl(context):
    mijn_bestand = open(context.filename, "at")
    context.mijn_bestand = mijn_bestand


@when(u'I write the following table in it')
def step_impl(context):
    mijn_bestand = context.mijn_bestand
    for row in context.table:
        course = row["course"]
        participant = row["participants"]
        mijn_bestand.write(course + "\t" + participant + "\n")
    mijn_bestand.close()


@then(u'This file has 3 lines in it')
def step_impl(context):
    mijn_bestand = open(context.filename, "rt")
    regels_in_bestand = mijn_bestand.readlines()
    aantal_regels = len(regels_in_bestand)

    assert aantal_regels == 3