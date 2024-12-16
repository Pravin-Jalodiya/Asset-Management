from dataclasses import dataclass


@dataclass
class CustomResponse:
    status_code: int
    message: str
    data: any

    def dto_to_dict(self):
        response ={
            'status_code': self.status_code,
            'message': self.message,
        }

        if self.data:
            response.update({'data': self.data})

        return response