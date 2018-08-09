form.save(commit=False)
            form.instance.author = self.request.user
            form.instance.content_type_id = self.get_content_type(model_name='comment').id
            form.instance.object_id = parent_id
            form.instance.parent_id = parent_id
            form.parent = Comment.objects.get(id=parent_id)
            form.save()

            response_data['author'] = form.instance.author.username
            response_data['pub_date'] = form.instance.pub_date
            response_data['text'] = form.instance.text
            response_data['reply_id'] = str(parent_i