from rest_framework import serializers
from .models import Form, Question, Response, Answer
import json

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())

    class Meta:
        model = Question
        fields = ['id', 'form', 'question_text', 'question_type', 'order', 'required', 'options']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['options'] = instance.get_options() if instance.options else []
        return representation

    def create(self, validated_data):
        options = validated_data.pop('options', None)
        instance = super().create(validated_data)
        if options:
            instance.options = json.dumps(options)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        options = validated_data.pop('options', None)
        instance = super().update(instance, validated_data)
        if options:
            instance.options = json.dumps(options)
            instance.save()
        return instance

class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'updated_at', 'questions']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['question', 'answer_text']

class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['id', 'form', 'submitted_at', 'answers']
        read_only_fields = ['submitted_at']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(response=response, **answer_data)
        return response
