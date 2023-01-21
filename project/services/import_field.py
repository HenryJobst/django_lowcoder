# Code is based on Field class of 'https://github.com/johncmacy/django-from-excel'
import sys
from typing import Final

from pandas import Series
from project.models import Field

DUPLICATES_AS_ENTITY_MIN_RATIO: Final[int] = 25


class ImportField:
    NULL: Final[str] = "null"
    BLANK: Final[str] = "blank"
    CHOICES: Final[str] = "choices"
    DECIMAL_PLACES: Final[str] = "decimal_places"
    MAX_DIGITS: Final[str] = "max_digits"
    MAX_LENGTH: Final[str] = "max_length"
    DEFAULT_VALUE: Final[str] = "default_value"

    def __init__(self, series: Series):
        self.field_name = series.name
        self.series = series
        self.is_nullable = self.series.hasnans
        self.series_without_nulls = Series([v for v in series.dropna()])
        self.dtype = str(self.series_without_nulls.dtype)
        self.duplicated = self.series_without_nulls.duplicated()
        self.has_duplicate_values = any(self.duplicated)
        self.duplicates = self.series_without_nulls.drop_duplicates()
        self.choices = None
        self.choices_reverse = None
        (
            self.field_type,
            self.kwargs,
            self.field_type_and_kwargs,
        ) = self.get_field_type_and_kwargs()

    def get_duplicate_compress_ratio(self):
        return (len(self.duplicates) * 100) / len(self.series_without_nulls)

    def get_field_type_and_kwargs(self):
        field_type: Field.Datatype = Field.Datatype.NONE
        kwargs = {
            self.CHOICES: None,
            self.MAX_DIGITS: None,
            self.MAX_LENGTH: None,
            self.DECIMAL_PLACES: None,
            self.NULL: False,
            self.BLANK: False,
            self.DEFAULT_VALUE: None,
        }

        if self.dtype == "object":
            ratio = self.get_duplicate_compress_ratio()
            if self.has_duplicate_values and ratio < DUPLICATES_AS_ENTITY_MIN_RATIO:
                field_type = Field.Datatype.INTEGER_FIELD
                self.choices = {
                    i: value
                    for (i, value) in enumerate(self.duplicates.values, start=1)
                }
                self.choices_reverse = {v: k for k, v in self.choices.items()}
                kwargs[self.CHOICES] = {k: v for k, v in self.choices.items()}

                self.series = Series(
                    [self.choices_reverse.get(value) for value in self.series]
                )

            else:
                field_type = Field.Datatype.CHAR_FIELD
                kwargs[self.MAX_LENGTH] = Field.find_next_step(
                    max(
                        [
                            len(str(cell_value))
                            for cell_value in self.series_without_nulls
                        ]
                        or [1]
                    )
                )

        elif self.dtype == "bool":
            field_type = Field.Datatype.BOOLEAN_FIELD

        elif self.dtype == "int64":
            field_type = Field.Datatype.INTEGER_FIELD

        elif self.dtype == "float64":
            field_type = Field.Datatype.DECIMAL_FIELD

            def num_digits_and_precision(value: str) -> tuple:
                total_digits = len(value.replace(".", ""))
                dot = value.find(".")
                decimals = value[dot + 1 :]
                decimal_len = len(decimals)

                return total_digits, decimal_len

            all_num_digits_and_precision = [
                num_digits_and_precision(str(cell_value))
                for cell_value in self.series_without_nulls
            ]
            max_digits = max([n for n, _ in all_num_digits_and_precision] or [2])
            decimal_places = max([n for _, n in all_num_digits_and_precision] or [1])

            kwargs[self.MAX_DIGITS] = max_digits
            kwargs[self.DECIMAL_PLACES] = decimal_places

        elif self.dtype == "datetime64[ns]" or self.dtype == "datetime64[ns, tz]":
            field_type = Field.Datatype.DATE_TIME_FIELD
        else:
            sys.stdout.write(f"unhandled dtype")

        if self.is_nullable:
            kwargs[self.NULL] = True
            kwargs[self.BLANK] = True

        field_type_ext = f"model.{field_type}({{}})"
        return (
            field_type,
            kwargs,
            field_type_ext.format(", ".join(f"{k}={v}" for k, v in kwargs.items())),
        )

    def __str__(self):
        return f"{self.field_name} = {self.field_type_and_kwargs}"
