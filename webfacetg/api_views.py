from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pydantic import ValidationError as PydanticValidationError

from .models import Lottery
from .validators import LotteryUpdateSchema


class LotteryUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lottery_id, *args, **kwargs):
        try:
            lottery = Lottery.objects.using("psql").get(id=lottery_id)
            schema_data = LotteryUpdateSchema.model_validate(lottery)
            print(type(schema_data), schema_data)
        except PydanticValidationError as e:
            return Response({"error": [error["msg"] for error in e.errors()]},
                            status=status.HTTP_400_BAD_REQUEST)
        data = schema_data.model_dump()
        return Response(data=data, status=status.HTTP_200_OK)

    def put(self, request, lottery_id, *args, **kwargs):
        instance = Lottery.objects.using("psql").get(id=lottery_id)
        data = request.data
        name = data.get("name", False)

        try:
            schema_data = LotteryUpdateSchema.model_validate(data)
        except PydanticValidationError as e:
            # Преобразуем ошибки в формат JSON
            error = []
            for err in e.errors():
                msg = err["msg"]
                if msg.startswith("Value error, ["):
                    msg = msg.split("[", 1)[1].split("]", 1)[0].strip("'")
                error.append({"field": " -> ".join(map(str, err["loc"])), "error": msg})
            fields = {
                "name": "Имя лотереи",
                "description": "Описание лотереи",
            }
            field = fields.get(error[0].get('field'))
            error = error[0].get('error')
            error_text = f"""Поле '{field}' -> {error}"""
            return Response({"error": error_text}, status=status.HTTP_400_BAD_REQUEST)

        for attr, value in schema_data.model_dump(exclude_unset=True).items():
            try:
                if value is not None:
                    setattr(instance, attr, value)
            except Exception:
                pass

        if name and Lottery.objects.using("psql").filter(name=name).exclude(id=lottery_id).exists():
            return Response(data={"error": "Такая лотерея уже существует"}, status=status.HTTP_400_BAD_REQUEST)

        instance.save(using="psql")
        return Response()

    def delete(self, request, lottery_id, *args, **kwargs):
        lottery = Lottery.objects.using("psql").filter(id=lottery_id).first()
        if lottery:
            lottery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
