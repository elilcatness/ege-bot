from src.utils import get_doc, get_json, process_files_links, extract_images_from_text
from src.templates import *


def _find_categories(number: int):
    data = get_json(CAT_TEMPLATE % number)
    return [cat['id'] for cat in data]


def _process_description(desc: str):
    desc = '\''.join(desc.split('changeImageFilePath(\'')[-1].split('\'')[:-1])
    for key, val in [('<sup>', '^'), ('</sup>', ''), ('<sub>', '_'), ('</sub>', ''),
                     ('&nbsp;', ' '), ('&times;', '×'), ('<br/>', '\n'), ('&not;', '¬'),
                     ('&and;', '⋀'), ('&or;', '⋁'), ('&ndash;', '–'), ('  ', '')]:
        desc = desc.replace(key, val)
    desc = process_files_links(desc)
    return extract_images_from_text(desc)


def _strip_answer(desc: str):
    return '\''.join(desc.split('changeImageFilePath(\'')[-1].split('\'')[:-1]).replace('<br/>', '\n')


def _extract_task_number(doc):
    target = 'Задание КИМ № '
    p_blocks = [p.text_content() for p in doc.xpath('//div[@class="center"]/p')]
    if not p_blocks:
        return None
    p = p_blocks[0]
    idx = p.find(target) + len(target)
    result = ''
    while p[idx].isdigit():
        result += p[idx]
        idx += 1
    return int(result) if result else None


def _parse_tasks_page(doc, number: int = None):
    if not number:
        number = _extract_task_number(doc)
    descriptions = doc.xpath('//td[@class="topicview"]')
    answers = doc.xpath('//td[@class="answer"]/div')
    output = []
    for desc, answer in zip(descriptions, answers):
        desc, images = _process_description(desc.text_content())
        task_id = answer.get('id')
        answer = _strip_answer(answer.text_content())
        output.append({'id': task_id, 'number': number, 'description': desc, 'answer': answer} if not images else
                      {'id': task_id, 'number': number, 'description': desc, 'answer': answer,
                       'images': ';'.join(images)})
    return output


def get_task_by_id(task_id: int):
    doc = get_doc(SEARCH_TEMPLATE % task_id)
    tasks = _parse_tasks_page(doc)
    return tasks[0] if tasks else None


def get_tasks_by_number(number: int):
    categories = _find_categories(number)
    suffix = '&' + '&'.join([f'cat{cat_id}=on' for cat_id in categories])
    doc = get_doc(ALL_TEMPLATE % number + suffix)
