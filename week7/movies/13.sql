SELECT DISTINCT(people.name)
FROM people
JOIN stars ON people.id = stars.person_id
JOIN movies ON stars.movie_id = movies.id
WHERE people.id IN
        (SELECT stars.person_id FROM stars WHERE stars.movie_id IN
            (SELECT stars.movie_id FROM stars WHERE stars.person_id IN
                (SELECT people.id FROM people WHERE people.name = "Kevin Bacon" AND people.birth = 1958)))
      AND people.id NOT IN
        (SELECT people.id FROM people WHERE people.name = "Kevin Bacon" AND people.birth = 1958);