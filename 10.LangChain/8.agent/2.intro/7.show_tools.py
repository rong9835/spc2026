from langchain_community.agent_toolkits.load_tools import get_all_tool_names

print('--- load_tools 를 통해서 가져올수 있는 모든 도구 ---')
names = sorted(get_all_tool_names())

for name in names:
    print(f" - {name}")

print(f"\n총 {len(names)} 개 가 현재 사용 가능")
