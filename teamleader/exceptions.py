class TeamleaderError(Exception):
    pass


class InvalidInputError(TeamleaderError):
    pass


class TeamleaderAPIError(TeamleaderError):

    def __init__(self, message, api_response):
        super(TeamleaderError, self).__init__(message)
        self.api_response = api_response


class TeamleaderUnauthorizedError(TeamleaderAPIError):
    pass


class TeamleaderRateLimitExceededError(TeamleaderAPIError):
    pass


class TeamleaderBadRequestError(TeamleaderAPIError):
    pass


class TeamleaderUnknownAPIError(TeamleaderAPIError):
    pass
