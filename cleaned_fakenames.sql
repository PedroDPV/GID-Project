SELECT
  -- Substituindo strings vazias por valores nulos e capitalizando as palavras
  IF(TRIM(GivenName) = '', NULL, INITCAP(GivenName)) AS GivenName,
  IF(TRIM(Surname) = '', NULL, INITCAP(Surname)) AS Surname,
  -- Traduzindo o gênero de inglês para português
  CASE Gender
    WHEN 'male' THEN 'masculino'
    WHEN 'female' THEN 'feminino'
    ELSE NULL
  END AS Gender,
  -- Capitalizando as cidades e removendo as aspas
  INITCAP(REGEXP_REPLACE(TRIM(City), r'^"|"$', '')) AS City,
  -- Capitalizando os estados e removendo as aspas
  INITCAP(REGEXP_REPLACE(TRIM(StateFull), r'^"|"$', '')) AS StateFull,
  ZipCode,
  EmailAddress,
  Username,
  CCType,
  CCNumber
FROM
  `terraform-366517.dataset_project.tbl_fakenames`
