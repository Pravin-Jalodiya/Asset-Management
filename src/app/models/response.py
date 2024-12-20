from dataclasses import dataclass


@dataclass
class CustomResponse:
    status_code: int
    message: str
    data: any = None

    def object_to_dict(self):
        response ={
            'status_code': self.status_code,
            'message': self.message,
        }

        if self.data is not None:
            response.update({'data': self.data})

        return response