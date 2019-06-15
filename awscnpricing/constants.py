from typing import Dict  # noqa


class Enum(object):
    """Very simple string enumeration implementation.

    Basic usage: `Colors = Enum('red', 'blue', 'green')  # Colors.RED == 'red'`

    You may also use kwargs to override accessor names.
    ```
    Years = Enum(one_year='1yr')  # Years.ONE_YEAR == '1yr'
    ```
    """
    def __init__(self, *args, **kwargs):  # type: (*str, **str) -> None
        self._values = {}  # type: Dict[str, str]
        for arg in args:
            self._values[arg.upper()] = arg
        for kwarg in kwargs:
            value = kwargs[kwarg]
            self._values[kwarg.upper()] = value

    def __getattr__(self, attr):
        if attr not in self._values:
            raise AttributeError("Enum value '{}' doesn't exist.".format(attr))
        return self._values[attr]

    def values(self):
        return self._values.values()


# noqa - Taken from: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
REGION_SHORTS = {
    'cn-northwest-1': 'China (Ningxia)',
    'cn-north-1': 'China (Beijing)'
}


EC2_LEASE_CONTRACT_LENGTH = Enum(one_year='1yr', three_year='3yr')
EC2_OFFERING_CLASS = Enum('standard', 'convertible')
EC2_PURCHASE_OPTION = Enum(
    no_upfront='No Upfront',
    partial_upfront='Partial Upfront',
    all_upfront='All Upfront'
)

RDS_LEASE_CONTRACT_LENGTH = Enum(one_year='1yr', three_year='3yr')
RDS_OFFERING_CLASS = Enum('standard')
RDS_PURCHASE_OPTION = Enum(
    no_upfront='No Upfront',
    partial_upfront='Partial Upfront',
    all_upfront='All Upfront'
)
