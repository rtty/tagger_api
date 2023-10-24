from rest_framework import serializers


class ProjectDetailsSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.CharField(source="_id")
    startDate = serializers.DateTimeField()
    endDate = serializers.DateTimeField()
    track = serializers.CharField()
    appealsEndDate = serializers.DateTimeField()
    tags = serializers.SerializerMethodField()
    winners = serializers.SerializerMethodField()

    @classmethod
    def get_tags(cls, project_details_obj):
        tags = []
        for t in project_details_obj.output_tag:
            tags.append(t.tag)
        return tags

    @classmethod
    def get_winners(cls, project_details_obj):
        winners = []
        for w in project_details_obj.winners:
            winners.append(
                {
                    "handle": w.handle,
                    "placement": w.placement,
                    "userId": w.userId,
                }
            )
        return winners


class ProjectTagsSerializer(serializers.Serializer):
    output_tag = serializers.SerializerMethodField()

    @classmethod
    def get_output_tag(cls, project_details_obj):
        output_tag = []
        for t in project_details_obj.output_tag:
            output_tag.append({"type": t.type, "tag": t.tag, "source": t.source})
        return output_tag
