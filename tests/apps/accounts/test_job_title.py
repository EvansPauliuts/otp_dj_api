import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import JobTitle

pytestmark = pytest.mark.django_db


class TestJobTitle:
    def test_job_list(self, job_title):
        assert job_title is not None

    def test_job_create(self, organization, business_unit):
        new_job_title = JobTitle.objects.create(
            organization=organization,
            business_unit=business_unit,
            status='A',
            name='Test Job Title',
            description='Another Description',
            job_function='SYS_ADMIN',
        )

        assert new_job_title is not None
        assert new_job_title.name == 'Test Job Title'
        assert new_job_title.description == 'Another Description'

    def test_job_update(self, job_title):
        job_title.name = 'test update'
        job_title.save()

        assert job_title.name == 'test update'

    def test_job_get(self, api_client):
        response = api_client.get(reverse('users:job_titles-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_job_post(self, api_client):
        response = api_client.post(
            reverse('users:job_titles-list'),
            {
                'name': 'test job title',
                'job_function': 'MANAGER',
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'test job title'
        assert response.data['job_function'] == 'MANAGER'

    def test_job_put(self, api_client, job_title):
        response = api_client.put(
            reverse(
                'users:job_titles-detail',
                kwargs={'pk': job_title.id},
            ),
            {'name': 'test job title', 'job_function': 'MANAGER'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'test job title'
        assert response.data['job_function'] == 'MANAGER'

    def test_job_delete(self, api_client, job_title):
        response = api_client.delete(
            reverse('users:job_titles-detail', kwargs={'pk': job_title.id}),
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None

    def test_job_detail(self, api_client, job_title):
        response = api_client.get(
            reverse(
                'users:job_titles-detail',
                kwargs={'pk': job_title.id},
            ),
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == job_title.name
        assert response.data['job_function'] == job_title.job_function

    def test_job_expand_is_true(self, api_client, job_title):
        response = api_client.get(
            reverse('users:job_titles-list') + '?expand_users=true',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['users'] is not None

    def test_job_expand_is_false(self, api_client, job_title):
        response = api_client.get(
            reverse('users:job_titles-list') + '?expand_users=false',
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'users' not in response.data['results'][0]

    def test_job_post_with_unique_name(self, api_client, job_title):
        job_title.name = 'test'
        job_title.save()

        job_title.refresh_from_db()

        response = api_client.post(
            reverse('users:job_titles-list'),
            {'name': 'test', 'job_function': 'MANAGER'},
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['type'] == 'validation_error'
        assert (
            response.data['errors'][0]['detail']
            == 'Job Title with this `name` already exists. Please try again.'
        )
