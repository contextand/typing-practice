export default function handler(req, res) {
  res.setHeader('Content-Type', 'text/yaml; charset=utf-8');
  res.send(`
backend:
  name: github
  repo: contextand/typing-practice
  branch: main
  base_url: https://api.decapcms.org

locale: ko
media_folder: admin/uploads

collections:
  - name: books
    label: 책
    label_singular: 책
    folder: data/책
    create: true
    slug: "{{title}}"
    format: frontmatter
    fields:
      - { label: 제목, name: title, widget: string }
      - { label: 글쓴이, name: author, widget: string, required: false }
      - { label: 장르, name: genre, widget: string, required: false }
      - { label: 출판사, name: publisher, widget: string, required: false }
      - { label: 정리한 날, name: date, widget: string, required: false, hint: "예: 2025년 1월 1일" }
      - { label: 발췌문, name: body, widget: text, hint: "페이지 번호와 발췌문을 번갈아 입력하세요." }
`.trim());
}
