"""A restrained width axis; interpolate identical cubic contour topology."""

from io import BytesIO

from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    SourceDescriptor,
)
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import build


def variable_font(static, output):
    source_bytes = BytesIO()
    static.save(source_bytes)
    design = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.name = "Width"
    axis.tag = "wdth"
    axis.minimum = 85
    axis.default = 100
    axis.maximum = 115
    design.addAxis(axis)
    for width in [85, 100, 115]:
        master = TTFont(BytesIO(source_bytes.getvalue()), recalcTimestamp=False)
        factor = width / 100
        glyphs = master.getGlyphSet()
        top = master["CFF "].cff.topDictIndex[0]
        for name in master.getGlyphOrder():
            advance, lsb = master["hmtx"][name]
            pen = T2CharStringPen(round(advance * factor), None, roundTolerance=0)
            glyphs[name].draw(TransformPen(pen, (factor, 0, 0, 1, 0, 0)))
            top.CharStrings[name] = pen.getCharString(
                private=top.Private, globalSubrs=top.GlobalSubrs
            )
            master["hmtx"][name] = (round(advance * factor), round(lsb * factor))
        top.Private.StdVW = round(66 * factor)
        # Kern values and cursor positions follow the same horizontal geometry.
        for lookup in master["GPOS"].table.LookupList.Lookup:
            if lookup.LookupType != 2:
                continue
            for sub in lookup.SubTable:
                records = (
                    [record for pair in sub.PairSet for record in pair.PairValueRecord]
                    if sub.Format == 1
                    else [
                        record
                        for row in sub.Class1Record
                        for record in row.Class2Record
                    ]
                )
                for record in records:
                    for value in [record.Value1, record.Value2]:
                        if value:
                            for field in ["XAdvance", "XPlacement"]:
                                if hasattr(value, field):
                                    setattr(
                                        value,
                                        field,
                                        round(getattr(value, field) * factor),
                                    )
        for lig in master["GDEF"].table.LigCaretList.LigGlyph:
            for caret in lig.CaretValue:
                caret.Coordinate = round(caret.Coordinate * factor)
        for name_id, value in [
            (1, "Bathys Variable"),
            (3, "BathysVariable-1.500"),
            (4, "Bathys Variable"),
            (6, "BathysVariable-Regular"),
            (16, "Bathys Variable"),
            (17, "Regular"),
        ]:
            master["name"].setName(value, name_id, 3, 1, 0x409)
        top.FamilyName = "Bathys Variable"
        top.FullName = "Bathys Variable"
        source = SourceDescriptor()
        source.font = master
        source.name = f"width-{width}"
        source.familyName = "Bathys Variable"
        source.styleName = "Regular"
        source.location = {"Width": width}
        source.copyInfo = source.copyLib = source.copyFeatures = width == 100
        design.addSource(source)
    for width, label in [(85, "Narrow"), (100, "Regular"), (115, "Wide")]:
        instance = InstanceDescriptor()
        instance.name = label
        instance.styleName = label
        instance.familyName = "Bathys Variable"
        instance.location = {"Width": width}
        design.addInstance(instance)
    variable, _, _ = build(design)
    variable.recalcTimestamp = False
    variable.save(output / "Bathys-Variable.otf")
    variable.flavor = "woff2"
    variable.save(output / "Bathys-Variable.woff2")
