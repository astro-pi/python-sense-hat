class SenseHatException(Exception):
    """
    The base exception class for all SenseHat exceptions.
    """
    fmt = 'An unspecified error occurred'

    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs


class ColourSensorInitialisationError(SenseHatException):
    fmt = "Failed to initialise colour sensor. {explanation}"


class InvalidGainError(SenseHatException):
    fmt = "Cannot set gain to '{gain}'. Values: {values}"


class InvalidIntegrationCyclesError(SenseHatException):
    fmt = "Cannot set integration cycles to {integration_cycles} (1-256)"
