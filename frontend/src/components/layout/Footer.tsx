export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col md:flex-row justify-between gap-8">
          {/* Logo & Description */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xl">⛰️</span>
              <span className="font-bold text-gray-900">100대 명산 카탈로그</span>
            </div>
            <p className="text-sm text-gray-500 max-w-xs">
              블랙야크 100대 명산 챌린지를 위한 종합 정보 플랫폼
            </p>
          </div>

          {/* Links */}
          <div className="flex gap-12">
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">서비스</h4>
              <ul className="space-y-2 text-sm text-gray-500">
                <li>
                  <a href="/" className="hover:text-gray-700 transition-colors">산 목록</a>
                </li>
                <li>
                  <a href="/dashboard" className="hover:text-gray-700 transition-colors">내 기록</a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">참고</h4>
              <ul className="space-y-2 text-sm text-gray-500">
                <li>
                  <a
                    href="https://bac.blackyak.com/BAC/ChallengeProgram/114"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-gray-700 transition-colors"
                  >
                    블랙야크 알파인클럽
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.forest.go.kr"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-gray-700 transition-colors"
                  >
                    산림청
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-10 pt-6 border-t border-gray-100 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-gray-400">
          <p>© 2024 대한민국 명산 탐험 카탈로그. All rights reserved.</p>
          <p>개인 프로젝트 · 비상업적 용도</p>
        </div>
      </div>
    </footer>
  );
}
